from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditEvent
from app.schemas import AuditEventResponse

router = APIRouter(tags=["Audit"])

@router.get("/audit/events", response_model=List[AuditEventResponse])
def get_audit_events(
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    actor: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    q = db.query(AuditEvent)
    if entity_type:
        q = q.filter(AuditEvent.entity_type == entity_type)
    if action:
        q = q.filter(AuditEvent.action == action)
    if actor:
        q = q.filter(AuditEvent.actor == actor)
    return q.order_by(AuditEvent.timestamp.desc()).offset(offset).limit(limit).all()

@router.get("/audit/entities/{entity_type}/{entity_id}", response_model=List[AuditEventResponse])
def get_entity_audit_events(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db)
):
    return (
        db.query(AuditEvent)
        .filter(
            AuditEvent.entity_type == entity_type,
            AuditEvent.entity_id == entity_id
        )
        .order_by(AuditEvent.timestamp.desc())
        .all()
    )
