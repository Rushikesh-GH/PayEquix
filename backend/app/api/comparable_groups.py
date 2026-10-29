from typing import List, Optional
import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ComparableGroup, ComparableGroupMember, SalaryRecord, Employee
from app.schemas import ComparableGroupResponse
from app.analytics.normalization import convert_currency, normalize_fte

router = APIRouter(tags=["Comparable Groups"])

@router.get("/comparable-groups", response_model=List[ComparableGroupResponse])
def get_comparable_groups(db: Session = Depends(get_db)):
    groups = db.query(ComparableGroup).all()
    res = []
    for g in groups:
        members = db.query(ComparableGroupMember).filter(
            ComparableGroupMember.group_id == g.group_id,
            ComparableGroupMember.is_active == True
        ).all()
        count = len(members)

        # Calculate group median/quartiles if count >= 5
        median_val = None
        q1_val = None
        q3_val = None

        if count >= g.min_size:
            member_ids = [m.employee_id for m in members]
            latest_salaries = (
                db.query(SalaryRecord)
                .filter(SalaryRecord.employee_id.in_(member_ids))
                .all()
            )
            # Normalization per employee
            norm_salaries = []
            for sr in latest_salaries:
                norm_salaries.append(sr.annualized_salary)
            if norm_salaries:
                median_val = round(float(np.median(norm_salaries)), 2)
                q1_val = round(float(np.percentile(norm_salaries, 25)), 2)
                q3_val = round(float(np.percentile(norm_salaries, 75)), 2)

        res.append(ComparableGroupResponse(
            group_id=g.group_id,
            group_code=g.group_code,
            group_name=g.group_name,
            role_id=g.role_id,
            level_id=g.level_id,
            location_zone=g.location_zone,
            min_size=g.min_size,
            is_active=g.is_active,
            equivalency_rationale=g.equivalency_rationale,
            approved_by=g.approved_by,
            is_equivalent_group=g.is_equivalent_group,
            created_at=g.created_at,
            member_count=count,
            median_normalized_salary=median_val,
            q1_salary=q1_val,
            q3_salary=q3_val
        ))
    return res

@router.get("/comparable-groups/{group_id}")
def get_comparable_group_detail(group_id: str, db: Session = Depends(get_db)):
    g = db.query(ComparableGroup).filter(ComparableGroup.group_id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Comparable group not found")

    members = (
        db.query(ComparableGroupMember)
        .filter(ComparableGroupMember.group_id == group_id)
        .all()
    )
    member_details = []
    for m in members:
        emp = db.query(Employee).filter(Employee.employee_id == m.employee_id).first()
        if emp:
            member_details.append({
                "employee_id": emp.employee_id,
                "name": f"{emp.first_name} {emp.last_name}",
                "role_id": emp.role_id,
                "role_name": emp.role.role_name if emp.role else emp.role_id,
                "level_id": emp.level_id,
                "level_name": emp.level.level_name if emp.level else emp.level_id,
                "location_id": emp.location_id,
                "fte": emp.fte,
                "employment_status": emp.employment_status,
                "is_active": m.is_active
            })

    return {
        "group": g,
        "member_count": len(members),
        "is_sufficient_sample": len(members) >= g.min_size,
        "members": member_details
    }
