import uuid
from datetime import datetime, date
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import (
    AdjustmentProposal, ApprovalEvent, AdjustmentApplicationEvent,
    SalaryRecord, Employee, CompensationBand, User
)
from app.audit.service import log_audit_event
from app.analytics.normalization import (
    convert_currency, normalize_fte, calculate_band_position, NormalizationError
)

class ProposalWorkflowService:
    def __init__(self, db: Session):
        self.db = db

    def create_proposal(
        self,
        creator: User,
        employee_id: str,
        proposed_salary: float,
        proposed_currency: Optional[str],
        reason_codes: str,
        evidence_summary: str,
        effective_date: Optional[date] = None
    ) -> AdjustmentProposal:
        """Create a new adjustment proposal in 'draft' status."""
        emp = self.db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")

        latest_salary = (
            self.db.query(SalaryRecord)
            .filter(SalaryRecord.employee_id == employee_id)
            .order_by(SalaryRecord.effective_date.desc())
            .first()
        )
        if not latest_salary:
            raise HTTPException(status_code=400, detail="Cannot propose adjustment for employee without salary record")

        curr = proposed_currency or latest_salary.currency_code
        band = (
            self.db.query(CompensationBand)
            .filter(
                CompensationBand.role_id == emp.role_id,
                CompensationBand.level_id == emp.level_id,
                CompensationBand.location_id == emp.location_id,
                CompensationBand.effective_start_date <= (effective_date or date.today()),
                (CompensationBand.effective_end_date.is_(None) | (CompensationBand.effective_end_date >= (effective_date or date.today())))
            )
            .first()
        )

        # Baseline calculations
        fte = emp.fte if 0.1 <= emp.fte <= 1.0 else 1.0
        norm_curr = latest_salary.annualized_salary / fte
        norm_prop = proposed_salary / fte

        pos_before = 50.0
        pos_after = 50.0
        if band:
            try:
                pos_before = calculate_band_position(norm_curr, band.minimum_salary, band.maximum_salary)
                pos_after = calculate_band_position(norm_prop, band.minimum_salary, band.maximum_salary)
            except Exception:
                pass

        adj_id = f"ADJ-2026-{uuid.uuid4().hex[:6].upper()}"
        proposal = AdjustmentProposal(
            adjustment_id=adj_id,
            employee_id=employee_id,
            salary_record_id=latest_salary.salary_record_id,
            applicable_band_id=band.band_id if band else None,
            proposed_salary=proposed_salary,
            proposed_currency=curr,
            normalized_current_salary=norm_curr,
            normalized_proposed_salary=norm_prop,
            reason_codes=reason_codes,
            evidence_summary=evidence_summary,
            estimated_band_position_before=pos_before,
            estimated_band_position_after=pos_after,
            proposal_status="draft",
            created_by=creator.username,
            created_at=datetime.utcnow(),
            effective_date=effective_date or date.today(),
            version_number=1
        )
        self.db.add(proposal)
        self.db.flush()

        log_audit_event(
            self.db,
            entity_type="ADJUSTMENT_PROPOSAL",
            entity_id=adj_id,
            action="CREATE_PROPOSAL",
            actor=creator.username,
            reason=f"Adjustment proposal created for {employee_id}",
            after_values={"proposed_salary": proposed_salary, "status": "draft"}
        )
        self.db.commit()
        return proposal

    def submit_proposal(self, proposal_id: str, actor: User, comments: str) -> AdjustmentProposal:
        """Transition: draft -> pending_review"""
        proposal = self.db.query(AdjustmentProposal).filter(AdjustmentProposal.adjustment_id == proposal_id).first()
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        if proposal.proposal_status not in ["draft", "returned_for_revision"]:
            raise HTTPException(status_code=400, detail=f"Cannot submit proposal with status '{proposal.proposal_status}'")

        prev = proposal.proposal_status
        proposal.proposal_status = "pending_review"
        proposal.version_number += 1

        event = ApprovalEvent(
            event_id=f"AE-{uuid.uuid4().hex[:10].upper()}",
            adjustment_id=proposal.adjustment_id,
            action="submitted",
            actor_user_id=actor.username,
            comments=comments,
            previous_status=prev,
            new_status="pending_review",
            created_at=datetime.utcnow()
        )
        self.db.add(event)
        log_audit_event(
            self.db, "ADJUSTMENT_PROPOSAL", proposal.adjustment_id, "SUBMIT",
            actor.username, comments, {"status": prev}, {"status": "pending_review"}
        )
        self.db.commit()
        return proposal

    def approve_proposal(self, proposal_id: str, actor: User, comments: str) -> AdjustmentProposal:
        """
        Transition: pending_review -> approved.
        Separation of duties: Creator cannot approve their own proposal!
        """
        proposal = self.db.query(AdjustmentProposal).filter(AdjustmentProposal.adjustment_id == proposal_id).first()
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        if proposal.proposal_status != "pending_review":
            raise HTTPException(status_code=400, detail=f"Cannot approve proposal with status '{proposal.proposal_status}'")

        # Separation of duties check
        if proposal.created_by == actor.username and actor.role != "system_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Separation of duties violation: Proposal creator cannot approve their own proposal."
            )

        prev = proposal.proposal_status
        proposal.proposal_status = "approved"
        proposal.approved_by = actor.username
        proposal.approved_at = datetime.utcnow()
        proposal.version_number += 1

        event = ApprovalEvent(
            event_id=f"AE-{uuid.uuid4().hex[:10].upper()}",
            adjustment_id=proposal.adjustment_id,
            action="approved",
            actor_user_id=actor.username,
            comments=comments,
            previous_status=prev,
            new_status="approved",
            created_at=datetime.utcnow()
        )
        self.db.add(event)
        log_audit_event(
            self.db, "ADJUSTMENT_PROPOSAL", proposal.adjustment_id, "APPROVE",
            actor.username, comments, {"status": prev}, {"status": "approved"}
        )
        self.db.commit()
        return proposal

    def reject_proposal(self, proposal_id: str, actor: User, comments: str) -> AdjustmentProposal:
        """Transition: pending_review -> rejected"""
        proposal = self.db.query(AdjustmentProposal).filter(AdjustmentProposal.adjustment_id == proposal_id).first()
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        if proposal.proposal_status != "pending_review":
            raise HTTPException(status_code=400, detail=f"Cannot reject proposal with status '{proposal.proposal_status}'")

        prev = proposal.proposal_status
        proposal.proposal_status = "rejected"
        proposal.version_number += 1

        event = ApprovalEvent(
            event_id=f"AE-{uuid.uuid4().hex[:10].upper()}",
            adjustment_id=proposal.adjustment_id,
            action="rejected",
            actor_user_id=actor.username,
            comments=comments,
            previous_status=prev,
            new_status="rejected",
            created_at=datetime.utcnow()
        )
        self.db.add(event)
        log_audit_event(
            self.db, "ADJUSTMENT_PROPOSAL", proposal.adjustment_id, "REJECT",
            actor.username, comments, {"status": prev}, {"status": "rejected"}
        )
        self.db.commit()
        return proposal

    def return_proposal(self, proposal_id: str, actor: User, comments: str) -> AdjustmentProposal:
        """Transition: pending_review -> returned_for_revision"""
        proposal = self.db.query(AdjustmentProposal).filter(AdjustmentProposal.adjustment_id == proposal_id).first()
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        if proposal.proposal_status != "pending_review":
            raise HTTPException(status_code=400, detail=f"Cannot return proposal with status '{proposal.proposal_status}'")

        prev = proposal.proposal_status
        proposal.proposal_status = "returned_for_revision"
        proposal.version_number += 1

        event = ApprovalEvent(
            event_id=f"AE-{uuid.uuid4().hex[:10].upper()}",
            adjustment_id=proposal.adjustment_id,
            action="returned_for_revision",
            actor_user_id=actor.username,
            comments=comments,
            previous_status=prev,
            new_status="returned_for_revision",
            created_at=datetime.utcnow()
        )
        self.db.add(event)
        log_audit_event(
            self.db, "ADJUSTMENT_PROPOSAL", proposal.adjustment_id, "RETURN_REVISION",
            actor.username, comments, {"status": prev}, {"status": "returned_for_revision"}
        )
        self.db.commit()
        return proposal

    def apply_proposal(self, proposal_id: str, actor: User, comments: str) -> Dict[str, Any]:
        """
        Transition: approved -> applied.
        Rules:
        - Must be in 'approved' status.
        - Cannot be applied twice.
        - Pending or rejected proposals CANNOT be applied.
        - Applying creates a new SalaryRecord (never overwrites existing).
        - Creates AdjustmentApplicationEvent.
        - Transactional safety with audit logging.
        """
        proposal = self.db.query(AdjustmentProposal).filter(AdjustmentProposal.adjustment_id == proposal_id).first()
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        if proposal.proposal_status == "applied":
            raise HTTPException(status_code=400, detail="This proposal has already been applied")

        # Scenario D enforcement: check approval
        if proposal.proposal_status != "approved":
            # Unauthorized adjustment attempt!
            log_audit_event(
                self.db,
                entity_type="ADJUSTMENT_PROPOSAL",
                entity_id=proposal_id,
                action="UNAUTHORIZED_APPLY_ATTEMPT",
                actor=actor.username,
                reason=f"Blocked attempt to apply unapproved proposal with status '{proposal.proposal_status}'"
            )
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot apply proposal in '{proposal.proposal_status}' status. Must be approved first."
            )

        # Check duplicate application
        existing_app = self.db.query(AdjustmentApplicationEvent).filter(
            AdjustmentApplicationEvent.adjustment_id == proposal_id
        ).first()
        if existing_app:
            raise HTTPException(status_code=400, detail="This proposal has already been applied")

        emp = self.db.query(Employee).filter(Employee.employee_id == proposal.employee_id).first()
        prev_salary_record = self.db.query(SalaryRecord).filter(
            SalaryRecord.salary_record_id == proposal.salary_record_id
        ).first()

        prev_salary_val = prev_salary_record.base_salary if prev_salary_record else 0.0
        eff_date = proposal.effective_date or date.today()

        # Create new salary record
        new_sr_id = f"SR-{uuid.uuid4().hex[:10].upper()}"
        new_salary_rec = SalaryRecord(
            salary_record_id=new_sr_id,
            employee_id=proposal.employee_id,
            salary_id=f"SAL-{proposal.employee_id}-{eff_date.strftime('%Y-%m')}",
            effective_date=eff_date,
            base_salary=proposal.proposed_salary,
            currency_code=proposal.proposed_currency,
            fte_at_record=emp.fte if emp else 1.0,
            annualized_salary=proposal.proposed_salary,
            salary_type="market_adjustment",
            source_event_id=proposal.adjustment_id,
            created_at=datetime.utcnow()
        )
        self.db.add(new_salary_rec)

        # Create AdjustmentApplicationEvent
        app_event = AdjustmentApplicationEvent(
            application_id=f"APP-{uuid.uuid4().hex[:10].upper()}",
            adjustment_id=proposal.adjustment_id,
            resulting_salary_record_id=new_sr_id,
            applied_by=actor.username,
            applied_at=datetime.utcnow(),
            previous_salary=prev_salary_val,
            new_salary=proposal.proposed_salary,
            currency_code=proposal.proposed_currency,
            effective_date=eff_date
        )
        self.db.add(app_event)

        # Update proposal state
        prev_status = proposal.proposal_status
        proposal.proposal_status = "applied"
        proposal.version_number += 1

        # Record approval transition event
        appr_event = ApprovalEvent(
            event_id=f"AE-{uuid.uuid4().hex[:10].upper()}",
            adjustment_id=proposal.adjustment_id,
            action="applied",
            actor_user_id=actor.username,
            comments=comments,
            previous_status=prev_status,
            new_status="applied",
            created_at=datetime.utcnow()
        )
        self.db.add(appr_event)

        # Audit event
        log_audit_event(
            self.db,
            entity_type="ADJUSTMENT_PROPOSAL",
            entity_id=proposal.adjustment_id,
            action="APPLY_ADJUSTMENT",
            actor=actor.username,
            reason=f"Applied adjustment to employee {proposal.employee_id}. New salary: {proposal.proposed_salary}",
            before_values={"salary": prev_salary_val, "status": prev_status},
            after_values={"salary": proposal.proposed_salary, "status": "applied", "salary_record_id": new_sr_id}
        )

        self.db.commit()
        return {
            "status": "applied",
            "adjustment_id": proposal.adjustment_id,
            "new_salary_record_id": new_sr_id,
            "new_salary": proposal.proposed_salary,
            "effective_date": str(eff_date)
        }
