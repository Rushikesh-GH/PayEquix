import json
import uuid
from datetime import datetime
from typing import Optional, Any, Dict
from sqlalchemy.orm import Session
from app.models import AuditEvent

def log_audit_event(
    db: Session,
    entity_type: str,
    entity_id: str,
    action: str,
    actor: str,
    reason: str,
    before_values: Optional[Dict[str, Any]] = None,
    after_values: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None
) -> AuditEvent:
    """
    Append-only audit logging for state changes and business decisions.
    Never overwrites or deletes existing audit events.
    """
    event = AuditEvent(
        event_id=f"AUD-{uuid.uuid4().hex[:12].upper()}",
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor=actor,
        timestamp=datetime.utcnow(),
        before_values=json.dumps(before_values, default=str) if before_values else None,
        after_values=json.dumps(after_values, default=str) if after_values else None,
        reason=reason,
        correlation_id=correlation_id or f"CORR-{uuid.uuid4().hex[:8].upper()}"
    )
    db.add(event)
    db.flush()
    return event
