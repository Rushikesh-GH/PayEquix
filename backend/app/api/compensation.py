from typing import List, Optional, Dict, Any
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    SalaryRecord, Employee, PerformanceEvidence, Tenure,
    Promotion, CompensationBand, DataQualityIssue, AdjustmentProposal
)
from app.schemas import (
    SalaryRecordResponse, CompensationAnalysisResult,
    EmployeeCompensationDetailResponse
)
from app.analytics.engine import DisparityAnalysisEngine

router = APIRouter(tags=["Compensation"])

@router.get("/salaries", response_model=List[SalaryRecordResponse])
def get_salaries(
    employee_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    q = db.query(SalaryRecord)
    if employee_id:
        q = q.filter(SalaryRecord.employee_id == employee_id)
    return q.order_by(SalaryRecord.effective_date.desc()).offset(offset).limit(limit).all()

@router.get("/employees/{employee_id}/salary-history", response_model=List[SalaryRecordResponse])
def get_employee_salary_history(employee_id: str, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return (
        db.query(SalaryRecord)
        .filter(SalaryRecord.employee_id == employee_id)
        .order_by(SalaryRecord.effective_date.desc())
        .all()
    )

@router.get("/employees/{employee_id}/compensation-analysis")
def get_employee_compensation_analysis(
    employee_id: str,
    as_of: Optional[date] = None,
    db: Session = Depends(get_db)
):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    engine = DisparityAnalysisEngine(db)
    analysis = engine.analyze_employee(emp, as_of_date=as_of or date(2026, 1, 1))

    # Fetch history & context
    salaries = (
        db.query(SalaryRecord)
        .filter(SalaryRecord.employee_id == employee_id)
        .order_by(SalaryRecord.effective_date.desc())
        .all()
    )
    performance = (
        db.query(PerformanceEvidence)
        .filter(PerformanceEvidence.employee_id == employee_id)
        .order_by(PerformanceEvidence.review_period_start.desc())
        .all()
    )
    tenure = (
        db.query(Tenure)
        .filter(Tenure.employee_id == employee_id)
        .all()
    )
    promotions = (
        db.query(Promotion)
        .filter(Promotion.employee_id == employee_id)
        .order_by(Promotion.effective_date.desc())
        .all()
    )
    issues = (
        db.query(DataQualityIssue)
        .filter(DataQualityIssue.entity_id == employee_id)
        .all()
    )
    proposals = (
        db.query(AdjustmentProposal)
        .filter(AdjustmentProposal.employee_id == employee_id)
        .order_by(AdjustmentProposal.created_at.desc())
        .all()
    )

    band = None
    if analysis.get("applicable_band_id"):
        band = db.query(CompensationBand).filter(CompensationBand.band_id == analysis["applicable_band_id"]).first()

    return {
        "analysis": analysis,
        "employee": {
            "employee_id": emp.employee_id,
            "employee_code": emp.employee_code,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "role_id": emp.role_id,
            "role_name": emp.role.role_name if emp.role else emp.role_id,
            "level_id": emp.level_id,
            "level_name": emp.level.level_name if emp.level else emp.level_id,
            "location_id": emp.location_id,
            "location_name": f"{emp.location.city}, {emp.location.country}" if emp.location else emp.location_id,
            "employment_type": emp.employment_type,
            "fte": emp.fte,
            "hire_date": emp.hire_date,
            "employment_status": emp.employment_status,
            "manager_employee_id": emp.manager_employee_id
        },
        "salary_history": salaries,
        "performance_history": performance,
        "tenure_history": tenure,
        "promotions": promotions,
        "applicable_band": band,
        "exceptions": issues,
        "proposals": proposals
    }

@router.get("/compensation/analysis")
def get_all_compensation_analysis(
    status: Optional[str] = None,
    role_id: Optional[str] = None,
    level_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db)
):
    engine = DisparityAnalysisEngine(db)
    all_res = engine.analyze_all()

    if status:
        all_res = [r for r in all_res if r["status"] == status]
    if role_id:
        all_res = [r for r in all_res if r["role_id"] == role_id]
    if level_id:
        all_res = [r for r in all_res if r["level_id"] == level_id]

    total = len(all_res)
    start = (page - 1) * page_size
    paged_items = all_res[start : start + page_size]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "items": paged_items
    }

@router.post("/compensation/analysis-runs")
def trigger_analysis_run(db: Session = Depends(get_db)):
    engine = DisparityAnalysisEngine(db)
    results = engine.analyze_all()
    review_candidates = sum(1 for r in results if r["status"] == "REVIEW_CANDIDATE")
    dq_issues = sum(1 for r in results if r["status"] == "DATA_QUALITY_EXCEPTION")
    return {
        "status": "COMPLETED",
        "employees_evaluated": len(results),
        "review_candidates_identified": review_candidates,
        "data_quality_exceptions": dq_issues,
        "timestamp": str(date.today())
    }
