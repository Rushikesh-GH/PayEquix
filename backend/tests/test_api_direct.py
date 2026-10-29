from app.main import health_check
from app.api.system import get_system_info
from app.api.master_data import get_roles, get_levels, get_locations
from app.database import SessionLocal
from app.analytics.normalization import annualize_salary, calculate_compa_ratio
from app.services.proposal_service import ProposalWorkflowService
from app.models import User

def test_api_direct_calls():
    # 1. Health
    h = health_check()
    assert h["status"] == "healthy"

    # 2. Info
    info = get_system_info()
    assert info["status"] == "OPERATIONAL"

    # 3. Master data
    db = SessionLocal()
    roles = get_roles(db)
    assert len(roles) == 25

    levels = get_levels(db)
    assert len(levels) == 8

    locs = get_locations(db)
    assert len(locs) == 10

    # 4. Proposal service workflow & separation of duties
    svc = ProposalWorkflowService(db)
    hr_user = db.query(User).filter(User.username == "hr_lead").first()
    admin_user = db.query(User).filter(User.username == "admin").first()

    # Create proposal
    prop = svc.create_proposal(
        creator=hr_user,
        employee_id="EMP-000001",
        proposed_salary=150000.0,
        proposed_currency="USD",
        reason_codes="MARKET_PARITY",
        evidence_summary="Strong performance review"
    )
    assert prop.proposal_status == "draft"

    # Submit
    prop = svc.submit_proposal(prop.adjustment_id, hr_user, "Submitting")
    assert prop.proposal_status == "pending_review"

    # Separation of duties: creator hr_lead cannot approve
    try:
        svc.approve_proposal(prop.adjustment_id, hr_user, "Self approve")
        assert False, "Should have raised exception for self-approval"
    except Exception as e:
        assert "Separation of duties" in str(e)

    # Legitimate approver approves
    prop = svc.approve_proposal(prop.adjustment_id, admin_user, "Approved")
    assert prop.proposal_status == "approved"

    # Apply
    res = svc.apply_proposal(prop.adjustment_id, admin_user, "Applied")
    assert res["status"] == "applied"

    db.close()
    print("ALL DIRECT API TESTS PASSED!")

if __name__ == "__main__":
    test_api_direct_calls()
