from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AdjustmentProposal, User
from app.schemas import (
    AdjustmentProposalResponse, AdjustmentProposalCreate, ProposalActionRequest
)
from app.security.auth import get_current_user, require_roles
from app.services.proposal_service import ProposalWorkflowService

router = APIRouter(tags=["Review Proposals"])

@router.get("/proposals", response_model=List[AdjustmentProposalResponse])
def get_proposals(
    status: Optional[str] = None,
    employee_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    q = db.query(AdjustmentProposal)
    if status:
        q = q.filter(AdjustmentProposal.proposal_status == status)
    if employee_id:
        q = q.filter(AdjustmentProposal.employee_id == employee_id)
    return q.order_by(AdjustmentProposal.created_at.desc()).offset(offset).limit(limit).all()

@router.get("/proposals/{adjustment_id}", response_model=AdjustmentProposalResponse)
def get_proposal(adjustment_id: str, db: Session = Depends(get_db)):
    prop = db.query(AdjustmentProposal).filter(AdjustmentProposal.adjustment_id == adjustment_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Adjustment proposal not found")
    return prop

@router.post("/proposals", response_model=AdjustmentProposalResponse)
def create_proposal(
    payload: AdjustmentProposalCreate,
    current_user: User = Depends(require_roles(["hr_partner", "system_admin"])),
    db: Session = Depends(get_db)
):
    svc = ProposalWorkflowService(db)
    return svc.create_proposal(
        creator=current_user,
        employee_id=payload.employee_id,
        proposed_salary=payload.proposed_salary,
        proposed_currency=payload.proposed_currency,
        reason_codes=payload.reason_codes,
        evidence_summary=payload.evidence_summary,
        effective_date=payload.effective_date
    )

@router.post("/proposals/{adjustment_id}/submit", response_model=AdjustmentProposalResponse)
def submit_proposal(
    adjustment_id: str,
    payload: ProposalActionRequest,
    current_user: User = Depends(require_roles(["hr_partner", "system_admin"])),
    db: Session = Depends(get_db)
):
    svc = ProposalWorkflowService(db)
    return svc.submit_proposal(adjustment_id, current_user, payload.comments)

@router.post("/proposals/{adjustment_id}/approve", response_model=AdjustmentProposalResponse)
def approve_proposal(
    adjustment_id: str,
    payload: ProposalActionRequest,
    current_user: User = Depends(require_roles(["hr_partner", "system_admin"])),
    db: Session = Depends(get_db)
):
    svc = ProposalWorkflowService(db)
    return svc.approve_proposal(adjustment_id, current_user, payload.comments)

@router.post("/proposals/{adjustment_id}/reject", response_model=AdjustmentProposalResponse)
def reject_proposal(
    adjustment_id: str,
    payload: ProposalActionRequest,
    current_user: User = Depends(require_roles(["hr_partner", "system_admin"])),
    db: Session = Depends(get_db)
):
    svc = ProposalWorkflowService(db)
    return svc.reject_proposal(adjustment_id, current_user, payload.comments)

@router.post("/proposals/{adjustment_id}/return", response_model=AdjustmentProposalResponse)
def return_proposal(
    adjustment_id: str,
    payload: ProposalActionRequest,
    current_user: User = Depends(require_roles(["hr_partner", "system_admin"])),
    db: Session = Depends(get_db)
):
    svc = ProposalWorkflowService(db)
    return svc.return_proposal(adjustment_id, current_user, payload.comments)

@router.post("/proposals/{adjustment_id}/apply")
def apply_proposal(
    adjustment_id: str,
    payload: ProposalActionRequest,
    current_user: User = Depends(require_roles(["hr_partner", "system_admin"])),
    db: Session = Depends(get_db)
):
    svc = ProposalWorkflowService(db)
    return svc.apply_proposal(adjustment_id, current_user, payload.comments)
