from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Employee, Role, Level, Location, CompensationBand
from app.schemas import (
    EmployeeDetailResponse, RoleResponse, LevelResponse,
    LocationResponse, CompensationBandResponse
)

router = APIRouter(tags=["Master Data"])

@router.get("/roles", response_model=List[RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()

@router.get("/levels", response_model=List[LevelResponse])
def get_levels(db: Session = Depends(get_db)):
    return db.query(Level).order_by(Level.level_rank.asc()).all()

@router.get("/locations", response_model=List[LocationResponse])
def get_locations(db: Session = Depends(get_db)):
    return db.query(Location).all()

@router.get("/bands", response_model=List[CompensationBandResponse])
def get_bands(
    role_id: Optional[str] = None,
    level_id: Optional[str] = None,
    location_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    q = db.query(CompensationBand)
    if role_id:
        q = q.filter(CompensationBand.role_id == role_id)
    if level_id:
        q = q.filter(CompensationBand.level_id == level_id)
    if location_id:
        q = q.filter(CompensationBand.location_id == location_id)
    return q.offset(offset).limit(limit).all()

@router.get("/bands/{band_id}", response_model=CompensationBandResponse)
def get_band(band_id: str, db: Session = Depends(get_db)):
    band = db.query(CompensationBand).filter(CompensationBand.band_id == band_id).first()
    if not band:
        raise HTTPException(status_code=404, detail="Compensation band not found")
    return band

@router.get("/employees")
def get_employees(
    search: Optional[str] = None,
    role_id: Optional[str] = None,
    level_id: Optional[str] = None,
    location_id: Optional[str] = None,
    employment_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db)
):
    q = db.query(Employee)
    if search:
        search_fmt = f"%{search}%"
        q = q.filter(
            or_(
                Employee.employee_id.ilike(search_fmt),
                Employee.employee_code.ilike(search_fmt),
                Employee.first_name.ilike(search_fmt),
                Employee.last_name.ilike(search_fmt)
            )
        )
    if role_id:
        q = q.filter(Employee.role_id == role_id)
    if level_id:
        q = q.filter(Employee.level_id == level_id)
    if location_id:
        q = q.filter(Employee.location_id == location_id)
    if employment_type:
        q = q.filter(Employee.employment_type == employment_type)
    if status:
        q = q.filter(Employee.employment_status == status)

    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    # Pre-fetch details
    res_items = []
    for emp in items:
        res_items.append({
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
        })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "items": res_items
    }

@router.get("/employees/{employee_id}", response_model=EmployeeDetailResponse)
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp
