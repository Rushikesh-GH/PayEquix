from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Date, DateTime, Text,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from app.database import Base

class Role(Base):
    __tablename__ = "roles"

    role_id = Column(String(50), primary_key=True)
    role_code = Column(String(50), unique=True, nullable=False, index=True)
    role_name = Column(String(100), nullable=False)
    job_family = Column(String(50), nullable=False, index=True)
    job_function = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    active_status = Column(Boolean, default=True, nullable=False)

    employees = relationship("Employee", back_populates="role")
    bands = relationship("CompensationBand", back_populates="role")


class Level(Base):
    __tablename__ = "levels"

    level_id = Column(String(50), primary_key=True)
    level_code = Column(String(50), unique=True, nullable=False, index=True)
    level_name = Column(String(100), nullable=False)
    level_rank = Column(Integer, nullable=False, index=True)
    career_track = Column(String(50), nullable=False)  # individual_contributor, management, specialist
    active_status = Column(Boolean, default=True, nullable=False)

    employees = relationship("Employee", back_populates="level")
    bands = relationship("CompensationBand", back_populates="level")


class Location(Base):
    __tablename__ = "locations"

    location_id = Column(String(50), primary_key=True)
    location_code = Column(String(50), unique=True, nullable=False, index=True)
    city = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    currency_code = Column(String(10), nullable=False, index=True)
    cost_of_labor_zone = Column(String(50), nullable=False, index=True)
    active_status = Column(Boolean, default=True, nullable=False)

    employees = relationship("Employee", back_populates="location")
    bands = relationship("CompensationBand", back_populates="location")


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    rate_id = Column(String(50), primary_key=True)
    from_currency = Column(String(10), nullable=False, index=True)
    to_currency = Column(String(10), nullable=False, index=True)
    rate = Column(Float, nullable=False)
    effective_date = Column(Date, nullable=False, index=True)
    source = Column(String(50), default="ECB_REFERENCE", nullable=False)

    __table_args__ = (
        Index("ix_exchange_lookup", "from_currency", "to_currency", "effective_date"),
    )


class CompensationBand(Base):
    __tablename__ = "compensation_bands"

    band_id = Column(String(100), primary_key=True)
    role_id = Column(String(50), ForeignKey("roles.role_id"), nullable=False, index=True)
    level_id = Column(String(50), ForeignKey("levels.level_id"), nullable=False, index=True)
    location_id = Column(String(50), ForeignKey("locations.location_id"), nullable=False, index=True)
    effective_start_date = Column(Date, nullable=False, index=True)
    effective_end_date = Column(Date, nullable=True, index=True)
    minimum_salary = Column(Float, nullable=False)
    midpoint_salary = Column(Float, nullable=False)
    maximum_salary = Column(Float, nullable=False)
    currency_code = Column(String(10), nullable=False)
    annual_basis = Column(Boolean, default=True, nullable=False)
    band_version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    role = relationship("Role", back_populates="bands")
    level = relationship("Level", back_populates="bands")
    location = relationship("Location", back_populates="bands")

    __table_args__ = (
        CheckConstraint("minimum_salary < midpoint_salary AND midpoint_salary < maximum_salary", name="chk_band_ordering"),
        Index("ix_band_lookup", "role_id", "level_id", "location_id", "effective_start_date"),
    )


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String(50), primary_key=True)  # EMP-000001
    employee_code = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role_id = Column(String(50), ForeignKey("roles.role_id"), nullable=False, index=True)
    level_id = Column(String(50), ForeignKey("levels.level_id"), nullable=False, index=True)
    location_id = Column(String(50), ForeignKey("locations.location_id"), nullable=False, index=True)
    employment_type = Column(String(50), default="full_time", nullable=False)  # full_time, part_time, contract
    fte = Column(Float, default=1.0, nullable=False)
    hire_date = Column(Date, nullable=False, index=True)
    termination_date = Column(Date, nullable=True)
    employment_status = Column(String(50), default="active", nullable=False, index=True)  # active, on_leave, terminated
    manager_employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    role = relationship("Role", back_populates="employees")
    level = relationship("Level", back_populates="employees")
    location = relationship("Location", back_populates="employees")
    manager = relationship("Employee", remote_side=[employee_id], backref="direct_reports")
    salaries = relationship("SalaryRecord", back_populates="employee", order_by="SalaryRecord.effective_date.asc()")
    performance_reviews = relationship("PerformanceEvidence", back_populates="employee")
    tenure_records = relationship("Tenure", back_populates="employee")
    promotions = relationship("Promotion", back_populates="employee")

    __table_args__ = (
        CheckConstraint("fte >= 0.1 AND fte <= 1.0", name="chk_employee_fte_range"),
    )


class SalaryRecord(Base):
    __tablename__ = "salary_records"

    salary_record_id = Column(String(50), primary_key=True)  # SR-000001
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=False, index=True)
    salary_id = Column(String(100), nullable=False, index=True)  # SAL-<employee-id>-2026-01
    effective_date = Column(Date, nullable=False, index=True)
    base_salary = Column(Float, nullable=False)
    currency_code = Column(String(10), nullable=False)
    fte_at_record = Column(Float, default=1.0, nullable=False)
    annualized_salary = Column(Float, nullable=False)
    salary_type = Column(String(50), default="base_salary", nullable=False)  # base_salary, merit_increase, promotion, market_adjustment
    source_event_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    employee = relationship("Employee", back_populates="salaries")

    __table_args__ = (
        CheckConstraint("base_salary > 0", name="chk_salary_positive"),
        CheckConstraint("fte_at_record >= 0.1 AND fte_at_record <= 1.0", name="chk_salary_fte_range"),
        Index("ix_salary_emp_date", "employee_id", "effective_date"),
    )


class PerformanceEvidence(Base):
    __tablename__ = "performance_evidence"

    evidence_id = Column(String(50), primary_key=True)  # PEV-000001
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=False, index=True)
    review_period_start = Column(Date, nullable=False)
    review_period_end = Column(Date, nullable=False)
    performance_rating = Column(Float, nullable=False)
    rating_scale_min = Column(Float, default=1.0, nullable=False)
    rating_scale_max = Column(Float, default=5.0, nullable=False)
    evidence_category = Column(String(50), nullable=False)  # annual_review, peer_feedback, manager_assessment
    documented_summary = Column(Text, nullable=False)
    source_reference = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    employee = relationship("Employee", back_populates="performance_reviews")

    __table_args__ = (
        CheckConstraint("performance_rating >= rating_scale_min AND performance_rating <= rating_scale_max", name="chk_rating_range"),
    )


class Tenure(Base):
    __tablename__ = "tenure"

    tenure_id = Column(String(50), primary_key=True)  # TEN-000001
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=False, index=True)
    tenure_start_date = Column(Date, nullable=False)
    tenure_end_date = Column(Date, nullable=True)
    tenure_type = Column(String(50), default="company_tenure", nullable=False)  # company_tenure, prior_relevant_experience
    relevant_experience_months = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    employee = relationship("Employee", back_populates="tenure_records")


class Promotion(Base):
    __tablename__ = "promotions"

    promotion_id = Column(String(50), primary_key=True)  # PROM-000001
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=False, index=True)
    previous_role_id = Column(String(50), ForeignKey("roles.role_id"), nullable=False)
    new_role_id = Column(String(50), ForeignKey("roles.role_id"), nullable=False)
    previous_level_id = Column(String(50), ForeignKey("levels.level_id"), nullable=False)
    new_level_id = Column(String(50), ForeignKey("levels.level_id"), nullable=False)
    effective_date = Column(Date, nullable=False, index=True)
    previous_salary_record_id = Column(String(50), nullable=True)
    resulting_salary_record_id = Column(String(50), nullable=True)
    promotion_status = Column(String(50), default="completed", nullable=False)  # completed, pending, rescinded
    documented_reason = Column(Text, nullable=False)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    employee = relationship("Employee", back_populates="promotions")


class ComparableGroup(Base):
    __tablename__ = "comparable_groups"

    group_id = Column(String(50), primary_key=True)  # GRP-000001
    group_code = Column(String(50), unique=True, nullable=False, index=True)
    group_name = Column(String(100), nullable=False)
    role_id = Column(String(50), ForeignKey("roles.role_id"), nullable=False)
    level_id = Column(String(50), ForeignKey("levels.level_id"), nullable=False)
    location_zone = Column(String(50), nullable=False)
    min_size = Column(Integer, default=5, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    equivalency_rationale = Column(Text, nullable=True)
    approved_by = Column(String(100), nullable=True)
    is_equivalent_group = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    members = relationship("ComparableGroupMember", back_populates="group")


class ComparableGroupMember(Base):
    __tablename__ = "comparable_group_members"

    member_id = Column(String(50), primary_key=True)  # GM-000001
    group_id = Column(String(50), ForeignKey("comparable_groups.group_id"), nullable=False, index=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=False, index=True)
    effective_start_date = Column(Date, nullable=False)
    effective_end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    group = relationship("ComparableGroup", back_populates="members")


class AdjustmentProposal(Base):
    __tablename__ = "adjustment_proposals"

    adjustment_id = Column(String(50), primary_key=True)  # ADJ-2026-000001
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=False, index=True)
    salary_record_id = Column(String(50), ForeignKey("salary_records.salary_record_id"), nullable=False)
    applicable_band_id = Column(String(100), nullable=True)
    proposed_salary = Column(Float, nullable=False)
    proposed_currency = Column(String(10), nullable=False)
    normalized_current_salary = Column(Float, nullable=False)
    normalized_proposed_salary = Column(Float, nullable=False)
    reason_codes = Column(Text, nullable=False)  # JSON or comma-separated
    evidence_summary = Column(Text, nullable=False)
    estimated_band_position_before = Column(Float, nullable=False)
    estimated_band_position_after = Column(Float, nullable=False)
    proposal_status = Column(String(50), default="draft", nullable=False, index=True)  # draft, pending_review, approved, rejected, returned_for_revision, applied
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    effective_date = Column(Date, nullable=True)
    version_number = Column(Integer, default=1, nullable=False)

    approval_events = relationship("ApprovalEvent", back_populates="proposal", order_by="ApprovalEvent.created_at.asc()")
    applications = relationship("AdjustmentApplicationEvent", back_populates="proposal")


class ApprovalEvent(Base):
    __tablename__ = "approval_events"

    event_id = Column(String(50), primary_key=True)  # AE-000001
    adjustment_id = Column(String(50), ForeignKey("adjustment_proposals.adjustment_id"), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # submitted, approved, rejected, returned_for_revision, applied
    actor_user_id = Column(String(100), nullable=False)
    comments = Column(Text, nullable=False)
    previous_status = Column(String(50), nullable=False)
    new_status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    proposal = relationship("AdjustmentProposal", back_populates="approval_events")


class AdjustmentApplicationEvent(Base):
    __tablename__ = "adjustment_application_events"

    application_id = Column(String(50), primary_key=True)  # APP-000001
    adjustment_id = Column(String(50), ForeignKey("adjustment_proposals.adjustment_id"), nullable=False, index=True)
    resulting_salary_record_id = Column(String(50), nullable=True)
    applied_by = Column(String(100), nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    previous_salary = Column(Float, nullable=False)
    new_salary = Column(Float, nullable=False)
    currency_code = Column(String(10), nullable=False)
    effective_date = Column(Date, nullable=False)

    proposal = relationship("AdjustmentProposal", back_populates="applications")


class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"

    issue_id = Column(String(50), primary_key=True)  # DQI-000001
    issue_type = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), default="MEDIUM", nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    description = Column(Text, nullable=False)
    expected_behavior = Column(Text, nullable=False)
    observed_behavior = Column(Text, nullable=False)
    detection_rule = Column(String(100), nullable=False)
    status = Column(String(50), default="DETECTED", nullable=False, index=True)  # DETECTED, INVESTIGATED, RESOLVED, DISMISSED
    documented_rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    event_id = Column(String(50), primary_key=True)  # AUD-000001
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(100), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, APPROVE, REJECT, APPLY, SECURITY_OVERRIDE
    actor = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    before_values = Column(Text, nullable=True)  # JSON
    after_values = Column(Text, nullable=True)   # JSON
    reason = Column(Text, nullable=False)
    correlation_id = Column(String(100), nullable=False, index=True)


class GenerationRun(Base):
    __tablename__ = "generation_runs"

    run_id = Column(String(50), primary_key=True)  # RUN-000001
    seed = Column(Integer, nullable=False)
    generator_version = Column(String(50), nullable=False)
    profile = Column(String(50), nullable=False)
    employee_count = Column(Integer, nullable=False)
    output_checksum = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(50), primary_key=True)  # USR-001
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False)  # employee, manager, hr_partner, it_operations, system_admin
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
