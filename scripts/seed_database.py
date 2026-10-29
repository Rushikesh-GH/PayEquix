"""
Database Initialization & Seeder Script.
Reads generated CSV data and seeds the SQLite/PostgreSQL database via SQLAlchemy.
Populates standard demo user accounts.
"""

import sys
import csv
from datetime import datetime, date
from pathlib import Path

# Add backend directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.database import engine, SessionLocal, Base
from app.models import (
    Role, Level, Location, ExchangeRate, CompensationBand,
    Employee, SalaryRecord, PerformanceEvidence, Tenure, Promotion,
    ComparableGroup, ComparableGroupMember, AdjustmentProposal,
    ApprovalEvent, AdjustmentApplicationEvent, DataQualityIssue,
    AuditEvent, GenerationRun, User
)
from app.security.auth import get_password_hash

DATA_DIR = ROOT_DIR / "data" / "generated"

def parse_date(val):
    if not val or val == "None":
        return None
    try:
        return datetime.strptime(val[:10], "%Y-%m-%d").date()
    except Exception:
        return None

def parse_datetime(val):
    if not val or val == "None":
        return None
    try:
        clean = val.replace("Z", "")
        return datetime.fromisoformat(clean)
    except Exception:
        return datetime.utcnow()

def seed_database():
    print("Re-creating all database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 1. Seed Demo Users
        print("Seeding demo user accounts...")
        demo_users = [
            User(
                user_id="USR-ADMIN-01",
                username="admin",
                email="admin@company.example",
                hashed_password=get_password_hash("AdminPassword123!"),
                role="system_admin",
                full_name="System Administrator",
                is_active=True
            ),
            User(
                user_id="USR-HR-01",
                username="hr_lead",
                email="hr.lead@company.example",
                hashed_password=get_password_hash("HrPassword123!"),
                role="hr_partner",
                full_name="HR Lead Partner",
                is_active=True
            ),
            User(
                user_id="USR-MGR-01",
                username="dept_manager",
                email="manager@company.example",
                hashed_password=get_password_hash("ManagerPassword123!"),
                role="manager",
                full_name="Department Manager",
                is_active=True
            ),
            User(
                user_id="USR-AUD-01",
                username="auditor",
                email="auditor@company.example",
                hashed_password=get_password_hash("AuditorPassword123!"),
                role="it_operations",
                full_name="IT Operations Auditor",
                is_active=True
            ),
            User(
                user_id="USR-EMP-01",
                username="employee1",
                email="employee1@company.example",
                hashed_password=get_password_hash("EmployeePassword123!"),
                role="employee",
                full_name="Staff Employee",
                is_active=True
            )
        ]
        db.add_all(demo_users)
        db.commit()

        # 2. Roles
        print("Seeding Roles...")
        with open(DATA_DIR / "roles.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            roles = [Role(
                role_id=r["role_id"],
                role_code=r["role_code"],
                role_name=r["role_name"],
                job_family=r["job_family"],
                job_function=r["job_function"],
                description=r["description"],
                active_status=r["active_status"].lower() == "true"
            ) for r in reader]
            db.bulk_save_objects(roles)
            db.commit()

        # 3. Levels
        print("Seeding Levels...")
        with open(DATA_DIR / "levels.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            levels = [Level(
                level_id=r["level_id"],
                level_code=r["level_code"],
                level_name=r["level_name"],
                level_rank=int(r["level_rank"]),
                career_track=r["career_track"],
                active_status=r["active_status"].lower() == "true"
            ) for r in reader]
            db.bulk_save_objects(levels)
            db.commit()

        # 4. Locations
        print("Seeding Locations...")
        with open(DATA_DIR / "locations.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            locations = [Location(
                location_id=r["location_id"],
                location_code=r["location_code"],
                city=r["city"],
                region=r["region"],
                country=r["country"],
                currency_code=r["currency_code"],
                cost_of_labor_zone=r["cost_of_labor_zone"],
                active_status=r["active_status"].lower() == "true"
            ) for r in reader]
            db.bulk_save_objects(locations)
            db.commit()

        # 5. Exchange Rates
        print("Seeding Exchange Rates...")
        with open(DATA_DIR / "exchange_rates.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rates = [ExchangeRate(
                rate_id=r["rate_id"],
                from_currency=r["from_currency"],
                to_currency=r["to_currency"],
                rate=float(r["rate"]),
                effective_date=parse_date(r["effective_date"]),
                source=r["source"]
            ) for r in reader]
            db.bulk_save_objects(rates)
            db.commit()

        # 6. Compensation Bands
        print("Seeding Compensation Bands...")
        with open(DATA_DIR / "compensation_bands.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            bands = [CompensationBand(
                band_id=r["band_id"],
                role_id=r["role_id"],
                level_id=r["level_id"],
                location_id=r["location_id"],
                effective_start_date=parse_date(r["effective_start_date"]),
                effective_end_date=parse_date(r["effective_end_date"]),
                minimum_salary=float(r["minimum_salary"]),
                midpoint_salary=float(r["midpoint_salary"]),
                maximum_salary=float(r["maximum_salary"]),
                currency_code=r["currency_code"],
                annual_basis=r["annual_basis"].lower() == "true",
                band_version=int(r["band_version"]),
                created_at=parse_datetime(r["created_at"])
            ) for r in reader]
            db.bulk_save_objects(bands)
            db.commit()

        # 7. Employees
        print("Seeding Employees...")
        with open(DATA_DIR / "employees.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            employees = [Employee(
                employee_id=r["employee_id"],
                employee_code=r["employee_code"],
                first_name=r["first_name"],
                last_name=r["last_name"],
                role_id=r["role_id"],
                level_id=r["level_id"],
                location_id=r["location_id"],
                employment_type=r["employment_type"],
                fte=float(r["fte"]),
                hire_date=parse_date(r["hire_date"]),
                termination_date=parse_date(r["termination_date"]),
                employment_status=r["employment_status"],
                manager_employee_id=r["manager_employee_id"] if r["manager_employee_id"] != "None" and r["manager_employee_id"] else None,
                created_at=parse_datetime(r["created_at"]),
                updated_at=parse_datetime(r["updated_at"])
            ) for r in reader]
            db.bulk_save_objects(employees)
            db.commit()

        # 8. Salary Records
        print("Seeding Salary Records...")
        with open(DATA_DIR / "salary_records.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            salaries = [SalaryRecord(
                salary_record_id=r["salary_record_id"],
                employee_id=r["employee_id"],
                salary_id=r["salary_id"],
                effective_date=parse_date(r["effective_date"]),
                base_salary=float(r["base_salary"]),
                currency_code=r["currency_code"],
                fte_at_record=float(r["fte_at_record"]),
                annualized_salary=float(r["annualized_salary"]),
                salary_type=r["salary_type"],
                source_event_id=r["source_event_id"] if r["source_event_id"] != "None" else None,
                created_at=parse_datetime(r["created_at"])
            ) for r in reader]
            db.bulk_save_objects(salaries)
            db.commit()

        # 9. Performance Evidence
        print("Seeding Performance Evidence...")
        with open(DATA_DIR / "performance_evidence.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            reviews = [PerformanceEvidence(
                evidence_id=r["evidence_id"],
                employee_id=r["employee_id"],
                review_period_start=parse_date(r["review_period_start"]),
                review_period_end=parse_date(r["review_period_end"]),
                performance_rating=float(r["performance_rating"]),
                rating_scale_min=float(r["rating_scale_min"]),
                rating_scale_max=float(r["rating_scale_max"]),
                evidence_category=r["evidence_category"],
                documented_summary=r["documented_summary"],
                source_reference=r["source_reference"],
                created_at=parse_datetime(r["created_at"])
            ) for r in reader]
            db.bulk_save_objects(reviews)
            db.commit()

        # 10. Tenure
        print("Seeding Tenure...")
        with open(DATA_DIR / "tenure.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            tenure_list = [Tenure(
                tenure_id=r["tenure_id"],
                employee_id=r["employee_id"],
                tenure_start_date=parse_date(r["tenure_start_date"]),
                tenure_end_date=parse_date(r["tenure_end_date"]),
                tenure_type=r["tenure_type"],
                relevant_experience_months=int(r["relevant_experience_months"]),
                recorded_at=parse_datetime(r["recorded_at"])
            ) for r in reader]
            db.bulk_save_objects(tenure_list)
            db.commit()

        # 11. Promotions
        print("Seeding Promotions...")
        with open(DATA_DIR / "promotions.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            proms = [Promotion(
                promotion_id=r["promotion_id"],
                employee_id=r["employee_id"],
                previous_role_id=r["previous_role_id"],
                new_role_id=r["new_role_id"],
                previous_level_id=r["previous_level_id"],
                new_level_id=r["new_level_id"],
                effective_date=parse_date(r["effective_date"]),
                previous_salary_record_id=r["previous_salary_record_id"] if r["previous_salary_record_id"] != "None" else None,
                resulting_salary_record_id=r["resulting_salary_record_id"] if r["resulting_salary_record_id"] != "None" else None,
                promotion_status=r["promotion_status"],
                documented_reason=r["documented_reason"],
                approved_by=r["approved_by"] if r["approved_by"] != "None" else None,
                approved_at=parse_datetime(r["approved_at"]),
                created_at=parse_datetime(r["created_at"])
            ) for r in reader]
            db.bulk_save_objects(proms)
            db.commit()

        # 12. Comparable Groups
        print("Seeding Comparable Groups & Members...")
        with open(DATA_DIR / "comparable_groups.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            cgroups = [ComparableGroup(
                group_id=r["group_id"],
                group_code=r["group_code"],
                group_name=r["group_name"],
                role_id=r["role_id"],
                level_id=r["level_id"],
                location_zone=r["location_zone"],
                min_size=int(r["min_size"]),
                is_active=r["is_active"].lower() == "true",
                equivalency_rationale=r["equivalency_rationale"] if r["equivalency_rationale"] != "None" else None,
                approved_by=r["approved_by"] if r["approved_by"] != "None" else None,
                is_equivalent_group=r["is_equivalent_group"].lower() == "true",
                created_at=parse_datetime(r["created_at"])
            ) for r in reader]
            db.bulk_save_objects(cgroups)
            db.commit()

        with open(DATA_DIR / "comparable_group_members.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            cg_members = [ComparableGroupMember(
                member_id=r["member_id"],
                group_id=r["group_id"],
                employee_id=r["employee_id"],
                effective_start_date=parse_date(r["effective_start_date"]),
                effective_end_date=parse_date(r["effective_end_date"]),
                is_active=r["is_active"].lower() == "true"
            ) for r in reader]
            db.bulk_save_objects(cg_members)
            db.commit()

        # 13. Adjustment Proposals & Approvals
        print("Seeding Adjustment Proposals...")
        with open(DATA_DIR / "adjustment_proposals.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            props = [AdjustmentProposal(
                adjustment_id=r["adjustment_id"],
                employee_id=r["employee_id"],
                salary_record_id=r["salary_record_id"],
                applicable_band_id=r["applicable_band_id"] if r["applicable_band_id"] != "None" else None,
                proposed_salary=float(r["proposed_salary"]),
                proposed_currency=r["proposed_currency"],
                normalized_current_salary=float(r["normalized_current_salary"]),
                normalized_proposed_salary=float(r["normalized_proposed_salary"]),
                reason_codes=r["reason_codes"],
                evidence_summary=r["evidence_summary"],
                estimated_band_position_before=float(r["estimated_band_position_before"]),
                estimated_band_position_after=float(r["estimated_band_position_after"]),
                proposal_status=r["proposal_status"],
                created_by=r["created_by"],
                created_at=parse_datetime(r["created_at"]),
                reviewed_by=r["reviewed_by"] if r["reviewed_by"] != "None" else None,
                reviewed_at=parse_datetime(r["reviewed_at"]),
                approved_by=r["approved_by"] if r["approved_by"] != "None" else None,
                approved_at=parse_datetime(r["approved_at"]),
                effective_date=parse_date(r["effective_date"]),
                version_number=int(r["version_number"])
            ) for r in reader]
            db.bulk_save_objects(props)
            db.commit()

        with open(DATA_DIR / "approval_events.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            appr_events = [ApprovalEvent(
                event_id=r["event_id"],
                adjustment_id=r["adjustment_id"],
                action=r["action"],
                actor_user_id=r["actor_user_id"],
                comments=r["comments"],
                previous_status=r["previous_status"],
                new_status=r["new_status"],
                created_at=parse_datetime(r["created_at"])
            ) for r in reader]
            db.bulk_save_objects(appr_events)
            db.commit()

        # 14. Data Quality Issues
        print("Seeding Data Quality Issues...")
        with open(DATA_DIR / "data_quality_issues.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            dq_issues = [DataQualityIssue(
                issue_id=r["issue_id"],
                issue_type=r["issue_type"],
                entity_type=r["entity_type"],
                entity_id=r["entity_id"],
                severity=r["severity"],
                description=r["description"],
                expected_behavior=r["expected_behavior"],
                observed_behavior=r["observed_behavior"],
                detection_rule=r["detection_rule"],
                status=r["status"],
                documented_rationale=r["documented_rationale"],
                created_at=parse_datetime(r["created_at"]),
                resolved_at=parse_datetime(r["resolved_at"])
            ) for r in reader]
            db.bulk_save_objects(dq_issues)
            db.commit()

        # 15. Audit Events
        print("Seeding Audit Events...")
        with open(DATA_DIR / "audit_events.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            audits = [AuditEvent(
                event_id=r["event_id"],
                entity_type=r["entity_type"],
                entity_id=r["entity_id"],
                action=r["action"],
                actor=r["actor"],
                timestamp=parse_datetime(r["timestamp"]),
                before_values=r["before_values"] if r["before_values"] != "None" else None,
                after_values=r["after_values"] if r["after_values"] != "None" else None,
                reason=r["reason"],
                correlation_id=r["correlation_id"]
            ) for r in reader]
            db.bulk_save_objects(audits)
            db.commit()

        print("\nDatabase Seeding Complete! All entities successfully populated.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
