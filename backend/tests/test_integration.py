import pytest
from app.main import app, health_check
from app.api.system import get_system_info
from app.api.master_data import get_roles, get_levels, get_locations, get_employees
from app.api.compensation import get_all_compensation_analysis
from app.api.exceptions import get_exceptions
from app.database import SessionLocal
from app.services.proposal_service import ProposalWorkflowService
from app.models import User, Employee, SalaryRecord, AdjustmentProposal, CompensationBand
from app.analytics.engine import DisparityAnalysisEngine

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_health_check_endpoint():
    h = health_check()
    assert h["status"] == "healthy"

def test_system_info_endpoint():
    info = get_system_info()
    assert info["status"] == "OPERATIONAL"
    assert info["random_seed"] == 20261022

def test_master_data_queries(db):
    roles = get_roles(db)
    assert len(roles) == 25

    levels = get_levels(db)
    assert len(levels) == 8

    locs = get_locations(db)
    assert len(locs) == 10

def test_employee_explorer_query(db):
    res = get_employees(page=1, page_size=10, db=db)
    assert res["total"] > 0
    assert len(res["items"]) == 10

def test_disparity_analysis_engine(db):
    engine = DisparityAnalysisEngine(db)
    results = engine.analyze_all()
    assert len(results) > 0

    # Ensure all required metrics exist in result
    r0 = results[0]
    assert "compa_ratio" in r0
    assert "band_position" in r0
    assert "normalized_fte_salary" in r0

def test_exceptions_workbench_query(db):
    issues = get_exceptions(db=db)
    assert len(issues) > 0
    types = {i.issue_type for i in issues}
    # Verify core injected exception types are captured
    assert "EXPIRED_BAND" in types
    assert "NORMALIZATION_ERROR" in types
    assert "MISSING_EXCHANGE_RATE" in types
    assert "UNAUTHORIZED_ADJUSTMENT" in types
    assert "INVALID_COMPARABLE_GROUP" in types

def test_proposal_lifecycle_and_separation_of_duties(db):
    svc = ProposalWorkflowService(db)
    hr_user = db.query(User).filter(User.username == "hr_lead").first()
    admin_user = db.query(User).filter(User.username == "admin").first()

    # 1. Create Proposal
    prop = svc.create_proposal(
        creator=hr_user,
        employee_id="EMP-000002",
        proposed_salary=110000.0,
        proposed_currency="USD",
        reason_codes="MARKET_PARITY",
        evidence_summary="Strong performance review",
        effective_date=None
    )
    assert prop.proposal_status == "draft"

    # 2. Submit Proposal
    prop = svc.submit_proposal(prop.adjustment_id, hr_user, "Submitting for review")
    assert prop.proposal_status == "pending_review"

    # 3. Negative Test: Creator CANNOT approve their own proposal
    try:
        svc.approve_proposal(prop.adjustment_id, hr_user, "Self approval")
        assert False, "Self-approval must be blocked"
    except Exception as e:
        assert "Separation of duties" in str(e)

    # 4. Negative Test: Cannot apply unapproved proposal
    try:
        svc.apply_proposal(prop.adjustment_id, admin_user, "Applying unapproved")
        assert False, "Applying unapproved proposal must fail"
    except Exception as e:
        assert "Must be approved first" in str(e)

    # 5. Legitimate approver approves
    prop = svc.approve_proposal(prop.adjustment_id, admin_user, "Approved by admin")
    assert prop.proposal_status == "approved"

    # 6. Apply approved proposal
    app_res = svc.apply_proposal(prop.adjustment_id, admin_user, "Applying approved")
    assert app_res["status"] == "applied"
    assert "new_salary_record_id" in app_res

    # 7. Negative Test: Cannot apply twice
    try:
        svc.apply_proposal(prop.adjustment_id, admin_user, "Applying second time")
        assert False, "Applying twice must fail"
    except Exception as e:
        assert "already been applied" in str(e)
