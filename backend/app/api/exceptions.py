from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DataQualityIssue, User
from app.schemas import DataQualityIssueResponse, UpdateIssueStatusRequest
from app.security.auth import get_current_user, require_roles
from app.audit.service import log_audit_event

router = APIRouter(tags=["Exceptions"])

@router.get("/exceptions", response_model=List[DataQualityIssueResponse])
def get_exceptions(
    issue_type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    entity_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    q = db.query(DataQualityIssue)
    if issue_type:
        q = q.filter(DataQualityIssue.issue_type == issue_type)
    if severity:
        q = q.filter(DataQualityIssue.severity == severity)
    if status:
        q = q.filter(DataQualityIssue.status == status)
    if entity_id:
        q = q.filter(DataQualityIssue.entity_id == entity_id)

    return q.order_by(DataQualityIssue.created_at.desc()).offset(offset).limit(limit).all()

@router.get("/exceptions/{issue_id}", response_model=DataQualityIssueResponse)
def get_exception(issue_id: str, db: Session = Depends(get_db)):
    issue = db.query(DataQualityIssue).filter(DataQualityIssue.issue_id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Exception not found")
    return issue

@router.patch("/exceptions/{issue_id}/status", response_model=DataQualityIssueResponse)
def update_exception_status(
    issue_id: str,
    payload: UpdateIssueStatusRequest,
    current_user: User = Depends(require_roles(["hr_partner", "it_operations", "system_admin"])),
    db: Session = Depends(get_db)
):
    issue = db.query(DataQualityIssue).filter(DataQualityIssue.issue_id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Exception not found")

    valid_statuses = ["DETECTED", "INVESTIGATED", "RESOLVED", "DISMISSED"]
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")

    prev = issue.status
    issue.status = payload.status
    issue.documented_rationale = payload.rationale
    if payload.status in ["RESOLVED", "DISMISSED"]:
        issue.resolved_at = datetime.utcnow()

    log_audit_event(
        db,
        entity_type="DATA_QUALITY_ISSUE",
        entity_id=issue.issue_id,
        action="UPDATE_STATUS",
        actor=current_user.username,
        reason=payload.rationale,
        before_values={"status": prev},
        after_values={"status": payload.status}
    )
    db.commit()
    db.refresh(issue)
    return issue
