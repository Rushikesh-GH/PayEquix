from datetime import date, datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str
    role: str
    full_name: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    role: str
    full_name: str
    is_active: bool

    class Config:
        from_attributes = True


# --- Master Data Schemas ---
class RoleResponse(BaseModel):
    role_id: str
    role_code: str
    role_name: str
    job_family: str
    job_function: str
    description: Optional[str] = None
    active_status: bool

    class Config:
        from_attributes = True

class LevelResponse(BaseModel):
    level_id: str
    level_code: str
    level_name: str
    level_rank: int
    career_track: str
    active_status: bool

    class Config:
        from_attributes = True

class LocationResponse(BaseModel):
    location_id: str
    location_code: str
    city: str
    region: str
    country: str
    currency_code: str
    cost_of_labor_zone: str
    active_status: bool

    class Config:
        from_attributes = True

class CompensationBandResponse(BaseModel):
    band_id: str
    role_id: str
    level_id: str
    location_id: str
    effective_start_date: date
    effective_end_date: Optional[date] = None
    minimum_salary: float
    midpoint_salary: float
    maximum_salary: float
    currency_code: str
    annual_basis: bool
    band_version: int

    class Config:
        from_attributes = True


# --- Employee & Salary Schemas ---
class EmployeeBase(BaseModel):
    employee_id: str
    employee_code: str
    first_name: str
    last_name: str
    role_id: str
    level_id: str
    location_id: str
    employment_type: str
    fte: float
    hire_date: date
    termination_date: Optional[date] = None
    employment_status: str
    manager_employee_id: Optional[str] = None

class EmployeeDetailResponse(EmployeeBase):
    role: Optional[RoleResponse] = None
    level: Optional[LevelResponse] = None
    location: Optional[LocationResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SalaryRecordResponse(BaseModel):
    salary_record_id: str
    employee_id: str
    salary_id: str
    effective_date: date
    base_salary: float
    currency_code: str
    fte_at_record: float
    annualized_salary: float
    salary_type: str
    source_event_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PerformanceEvidenceResponse(BaseModel):
    evidence_id: str
    employee_id: str
    review_period_start: date
    review_period_end: date
    performance_rating: float
    rating_scale_min: float
    rating_scale_max: float
    evidence_category: str
    documented_summary: str
    source_reference: str
    created_at: datetime

    class Config:
        from_attributes = True

class TenureResponse(BaseModel):
    tenure_id: str
    employee_id: str
    tenure_start_date: date
    tenure_end_date: Optional[date] = None
    tenure_type: str
    relevant_experience_months: int
    recorded_at: datetime

    class Config:
        from_attributes = True

class PromotionResponse(BaseModel):
    promotion_id: str
    employee_id: str
    previous_role_id: str
    new_role_id: str
    previous_level_id: str
    new_level_id: str
    effective_date: date
    previous_salary_record_id: Optional[str] = None
    resulting_salary_record_id: Optional[str] = None
    promotion_status: str
    documented_reason: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- Analytics Schemas ---
class CompensationAnalysisResult(BaseModel):
    employee_id: str
    employee_name: str
    role_id: str
    role_name: str
    level_id: str
    level_name: str
    location_id: str
    location_name: str
    currency: str
    actual_base_salary: float
    fte: float
    annualized_salary: float
    reporting_currency: str
    exchange_rate: float
    normalized_fte_salary: float
    applicable_band_id: Optional[str] = None
    band_min: Optional[float] = None
    band_mid: Optional[float] = None
    band_max: Optional[float] = None
    compa_ratio: Optional[float] = None
    band_position: Optional[float] = None
    is_below_band: bool = False
    is_above_band: bool = False
    is_underpaid_midpoint: bool = False
    comparable_group_id: Optional[str] = None
    comparable_group_size: Optional[int] = None
    group_median_salary: Optional[float] = None
    is_group_outlier: bool = False
    status: str  # VALID, REVIEW_CANDIDATE, DATA_QUALITY_EXCEPTION
    exception_reasons: List[str] = []
    has_active_proposal: bool = False

class EmployeeCompensationDetailResponse(BaseModel):
    employee: EmployeeDetailResponse
    current_analysis: Optional[CompensationAnalysisResult] = None
    salary_history: List[SalaryRecordResponse] = []
    performance_history: List[PerformanceEvidenceResponse] = []
    tenure_history: List[TenureResponse] = []
    promotions: List[PromotionResponse] = []
    applicable_band: Optional[CompensationBandResponse] = None
    exceptions: List[Any] = []
    proposals: List[Any] = []


# --- Exception Schemas ---
class DataQualityIssueResponse(BaseModel):
    issue_id: str
    issue_type: str
    entity_type: str
    entity_id: str
    severity: str
    description: str
    expected_behavior: str
    observed_behavior: str
    detection_rule: str
    status: str
    documented_rationale: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UpdateIssueStatusRequest(BaseModel):
    status: str  # INVESTIGATED, RESOLVED, DISMISSED
    rationale: str


# --- Proposal & Workflow Schemas ---
class AdjustmentProposalCreate(BaseModel):
    employee_id: str
    proposed_salary: float
    proposed_currency: Optional[str] = None
    reason_codes: str
    evidence_summary: str
    effective_date: Optional[date] = None

class AdjustmentProposalResponse(BaseModel):
    adjustment_id: str
    employee_id: str
    salary_record_id: str
    applicable_band_id: Optional[str] = None
    proposed_salary: float
    proposed_currency: str
    normalized_current_salary: float
    normalized_proposed_salary: float
    reason_codes: str
    evidence_summary: str
    estimated_band_position_before: float
    estimated_band_position_after: float
    proposal_status: str
    created_by: str
    created_at: datetime
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    effective_date: Optional[date] = None
    version_number: int

    class Config:
        from_attributes = True

class ProposalActionRequest(BaseModel):
    comments: str

class ApprovalEventResponse(BaseModel):
    event_id: str
    adjustment_id: str
    action: str
    actor_user_id: str
    comments: str
    previous_status: str
    new_status: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Audit Schemas ---
class AuditEventResponse(BaseModel):
    event_id: str
    entity_type: str
    entity_id: str
    action: str
    actor: str
    timestamp: datetime
    before_values: Optional[str] = None
    after_values: Optional[str] = None
    reason: str
    correlation_id: str

    class Config:
        from_attributes = True


# --- Comparable Group Schemas ---
class ComparableGroupResponse(BaseModel):
    group_id: str
    group_code: str
    group_name: str
    role_id: str
    level_id: str
    location_zone: str
    min_size: int
    is_active: bool
    equivalency_rationale: Optional[str] = None
    approved_by: Optional[str] = None
    is_equivalent_group: bool
    created_at: datetime
    member_count: int = 0
    median_normalized_salary: Optional[float] = None
    q1_salary: Optional[float] = None
    q3_salary: Optional[float] = None

    class Config:
        from_attributes = True


# --- System & Dashboard Schemas ---
class SystemInfo(BaseModel):
    app_name: str
    version: str
    environment: str
    random_seed: int
    database_type: str
    status: str

class ExecutiveDashboardMetrics(BaseModel):
    total_employees: int
    valid_comparisons_count: int
    review_candidates_count: int
    data_quality_exceptions_count: int
    below_band_count: int
    above_band_count: int
    pending_proposals_count: int
    approved_proposals_count: int
    applied_proposals_count: int
    avg_compa_ratio: Optional[float] = None
    comparable_groups_count: int
    data_validation_status: str
    exception_type_counts: Dict[str, int]
    proposal_status_counts: Dict[str, int]
    compa_ratio_distribution: List[Dict[str, Any]]
    band_position_distribution: List[Dict[str, Any]]
    historical_trends: List[Dict[str, Any]]
