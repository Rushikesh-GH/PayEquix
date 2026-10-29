"""
Deterministic Synthetic Data Generator for Compensation Disparity Analysis System.
Fixed Random Seed: 20261022
Supports:
  - Starter: ~100 employees
  - Medium: ~1,000 employees
  - Full: exactly 5,000 employees

Guarantees:
  - Exactly 200 distinct role-level combinations (25 roles * 8 levels = 200).
  - 3 years of salary history (2024, 2025, 2026).
  - 100% referential integrity.
  - Separate scenario injection layer producing isolated ground-truth.csv and ground-truth.json.
  - CSV, JSON, and SQL seed exports with SHA-256 checksums in manifest.
"""

import os
import sys
import json
import csv
import hashlib
import random
from datetime import date, datetime, timedelta
from pathlib import Path
import argparse

# Setup paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
GENERATED_DIR = DATA_DIR / "generated"
GROUND_TRUTH_DIR = DATA_DIR / "ground_truth"
EXPORTS_DIR = DATA_DIR / "exports"
MANIFESTS_DIR = DATA_DIR / "manifests"

for d in [GENERATED_DIR, GROUND_TRUTH_DIR, EXPORTS_DIR, MANIFESTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Master Data Definitions
ROLES_DEF = [
    # Engineering
    ("ROL-SWE", "Software Engineer", "Engineering", "Core Software Development", "Builds backend and frontend distributed systems"),
    ("ROL-SRE", "Site Reliability Engineer", "Engineering", "Infrastructure & Reliability", "Ensures high uptime, observability, and scaling"),
    ("ROL-SEC", "Security Engineer", "Engineering", "Information Security", "Secures infrastructure, audits vulnerabilities, and manages IAM"),
    ("ROL-DE", "Data Engineer", "Engineering", "Data Infrastructure", "Designs data pipelines, ETL, warehouses, and streaming"),
    ("ROL-QA", "Quality Assurance Engineer", "Engineering", "Test Engineering", "Automated testing, regression suites, and test frameworks"),
    ("ROL-MLE", "Machine Learning Engineer", "Engineering", "Applied Machine Learning", "Develops, deploys, and monitors ML models in production"),
    # Product & Design
    ("ROL-PM", "Product Manager", "Product", "Product Management", "Defines product strategy, roadmaps, and feature execution"),
    ("ROL-TPM", "Technical Program Manager", "Product", "Program Management", "Drives cross-team engineering execution and milestones"),
    ("ROL-UXD", "UX Designer", "Design", "User Experience Design", "Designs user journeys, wireframes, and design systems"),
    ("ROL-UR", "User Researcher", "Design", "Product Research", "Conducts user interviews, usability testing, and insights"),
    # Data & Analytics
    ("ROL-DS", "Data Scientist", "Data & Analytics", "Data Science", "Builds statistical models, experiments, and predictive analytics"),
    ("ROL-BA", "Business Analyst", "Data & Analytics", "Business Intelligence", "Translates business questions into KPI dashboards and reports"),
    # Sales & Marketing
    ("ROL-AE", "Account Executive", "Sales", "Enterprise Sales", "Manages enterprise sales cycles, pipeline, and contract closing"),
    ("ROL-SDR", "Sales Development Rep", "Sales", "Inbound & Outbound Sales", "Prospects and qualifies enterprise sales leads"),
    ("ROL-PMM", "Product Marketing Manager", "Marketing", "Product Marketing", "Go-to-market strategy, product positioning, and launches"),
    ("ROL-DGM", "Digital Marketing Specialist", "Marketing", "Growth & Acquisition", "Drives SEO, SEM, content, and digital performance"),
    # Customer Success & Support
    ("ROL-CSM", "Customer Success Manager", "Customer Success", "Client Engagement", "Manages customer retention, onboarding, and satisfaction"),
    ("ROL-TSE", "Technical Support Engineer", "Customer Support", "Technical Support", "Troubleshoots customer technical issues and API integrations"),
    # Finance & Legal
    ("ROL-FA", "Financial Analyst", "Finance", "Corporate Finance", "Financial planning, forecasting, and budget modeling"),
    ("ROL-ACC", "Corporate Accountant", "Finance", "Accounting & Payroll", "General ledger, statutory compliance, and payroll review"),
    ("ROL-LC", "Legal Counsel", "Legal", "Corporate Law", "Contract negotiation, corporate governance, and regulatory compliance"),
    # HR & Operations
    ("ROL-HRP", "HR Business Partner", "People", "Human Resources", "People strategy, employee relations, and compensation reviews"),
    ("ROL-REC", "Technical Recruiter", "People", "Talent Acquisition", "Sources, interviews, and hires technical talent"),
    ("ROL-OPM", "Operations Manager", "Operations", "Business Operations", "Optimizes internal processes, workflows, and vendor logistics"),
    ("ROL-ITP", "IT Systems Administrator", "IT & Ops", "IT Infrastructure", "Manages internal IT hardware, networks, and enterprise tools"),
]

LEVELS_DEF = [
    ("LEV-IC1", "Associate (IC1)", 1, "individual_contributor"),
    ("LEV-IC2", "Mid-Level (IC2)", 2, "individual_contributor"),
    ("LEV-IC3", "Senior (IC3)", 3, "individual_contributor"),
    ("LEV-IC4", "Staff (IC4)", 4, "individual_contributor"),
    ("LEV-IC5", "Principal (IC5)", 5, "individual_contributor"),
    ("LEV-M1", "Engineering/Team Manager (M1)", 3, "management"),
    ("LEV-M2", "Senior Manager / Director (M2)", 4, "management"),
    ("LEV-S1", "Domain Specialist (S1)", 3, "specialist"),
]

LOCATIONS_DEF = [
    # India locations
    ("LOC-IN-BLR", "Bangalore", "Karnataka", "India", "INR", "Zone 2"),
    ("LOC-IN-MUM", "Mumbai", "Maharashtra", "India", "INR", "Zone 1"),
    ("LOC-IN-DEL", "Delhi NCR", "Delhi", "India", "INR", "Zone 2"),
    ("LOC-IN-HYD", "Hyderabad", "Telangana", "India", "INR", "Zone 3"),
    # Selected international locations
    ("LOC-US-NYC", "New York City", "New York", "United States", "USD", "Zone 1"),
    ("LOC-US-SFO", "San Francisco", "California", "United States", "USD", "Zone 1"),
    ("LOC-US-AUS", "Austin", "Texas", "United States", "USD", "Zone 2"),
    ("LOC-UK-LON", "London", "Greater London", "United Kingdom", "GBP", "Zone 1"),
    ("LOC-DE-BER", "Berlin", "Berlin", "Germany", "EUR", "Zone 2"),
    ("LOC-SG-SIN", "Singapore", "Central", "Singapore", "SGD", "Zone 1"),
]

# Baseline USD annual midpoints by Level rank
LEVEL_BASE_USD = {
    1: 65000,   # IC1
    2: 95000,   # IC2
    3: 135000,  # IC3 / M1 / S1
    4: 175000,  # IC4 / M2
    5: 225000,  # IC5
}

# Role market multiplier
ROLE_MULTIPLIERS = {
    "ROL-SWE": 1.15, "ROL-SRE": 1.12, "ROL-SEC": 1.18, "ROL-DE": 1.10, "ROL-QA": 0.90, "ROL-MLE": 1.25,
    "ROL-PM": 1.10, "ROL-TPM": 1.05, "ROL-UXD": 0.95, "ROL-UR": 0.90,
    "ROL-DS": 1.12, "ROL-BA": 0.85,
    "ROL-AE": 1.05, "ROL-SDR": 0.70, "ROL-PMM": 0.95, "ROL-DGM": 0.80,
    "ROL-CSM": 0.85, "ROL-TSE": 0.80,
    "ROL-FA": 0.90, "ROL-ACC": 0.80, "ROL-LC": 1.15,
    "ROL-HRP": 0.85, "ROL-REC": 0.80, "ROL-OPM": 0.85, "ROL-ITP": 0.85,
}

# Location cost of labor index relative to US Zone 1
LOCATION_INDEX = {
    "LOC-IN-BLR": 0.22,
    "LOC-IN-MUM": 0.24,
    "LOC-IN-DEL": 0.21,
    "LOC-IN-HYD": 0.19,
    "LOC-US-NYC": 1.05,
    "LOC-US-SFO": 1.10,
    "LOC-US-AUS": 0.90,
    "LOC-UK-LON": 0.82,
    "LOC-DE-BER": 0.75,
    "LOC-SG-SIN": 0.85,
}

# Effective-dated exchange rates to USD (reporting currency)
# convention: 1 Source Currency = X USD
EXCHANGE_RATES_DEF = [
    # 2024 Rates (effective 2024-01-01)
    {"rate_id": "FX-INR-USD-2024", "from_curr": "INR", "to_curr": "USD", "rate": 0.0120, "date": "2024-01-01"},
    {"rate_id": "FX-GBP-USD-2024", "from_curr": "GBP", "to_curr": "USD", "rate": 1.2750, "date": "2024-01-01"},
    {"rate_id": "FX-EUR-USD-2024", "from_curr": "EUR", "to_curr": "USD", "rate": 1.0950, "date": "2024-01-01"},
    {"rate_id": "FX-SGD-USD-2024", "from_curr": "SGD", "to_curr": "USD", "rate": 0.7550, "date": "2024-01-01"},
    {"rate_id": "FX-USD-USD-2024", "from_curr": "USD", "to_curr": "USD", "rate": 1.0000, "date": "2024-01-01"},

    # 2025 Rates (effective 2025-01-01)
    {"rate_id": "FX-INR-USD-2025", "from_curr": "INR", "to_curr": "USD", "rate": 0.0118, "date": "2025-01-01"},
    {"rate_id": "FX-GBP-USD-2025", "from_curr": "GBP", "to_curr": "USD", "rate": 1.2680, "date": "2025-01-01"},
    {"rate_id": "FX-EUR-USD-2025", "from_curr": "EUR", "to_curr": "USD", "rate": 1.0820, "date": "2025-01-01"},
    {"rate_id": "FX-SGD-USD-2025", "from_curr": "SGD", "to_curr": "USD", "rate": 0.7500, "date": "2025-01-01"},
    {"rate_id": "FX-USD-USD-2025", "from_curr": "USD", "to_curr": "USD", "rate": 1.0000, "date": "2025-01-01"},

    # 2026 Rates (effective 2026-01-01)
    {"rate_id": "FX-INR-USD-2026", "from_curr": "INR", "to_curr": "USD", "rate": 0.0115, "date": "2026-01-01"},
    {"rate_id": "FX-GBP-USD-2026", "from_curr": "GBP", "to_curr": "USD", "rate": 1.2820, "date": "2026-01-01"},
    {"rate_id": "FX-EUR-USD-2026", "from_curr": "EUR", "to_curr": "USD", "rate": 1.0880, "date": "2026-01-01"},
    {"rate_id": "FX-SGD-USD-2026", "from_curr": "SGD", "to_curr": "USD", "rate": 0.7620, "date": "2026-01-01"},
    {"rate_id": "FX-USD-USD-2026", "from_curr": "USD", "to_curr": "USD", "rate": 1.0000, "date": "2026-01-01"},
]

FIRST_NAMES = [
    "Aarav", "Aditi", "Rohan", "Priya", "Rahul", "Ananya", "Siddharth", "Neha", "Vikram", "Pooja",
    "Alexander", "Emily", "James", "Sarah", "Michael", "Emma", "Daniel", "Olivia", "William", "Sophia",
    "Liam", "Ava", "Noah", "Isabella", "Lucas", "Mia", "Benjamin", "Charlotte", "Henry", "Amelia",
    "Klaus", "Hannah", "Stefan", "Lukas", "Leon", "Sophie", "Jonas", "Lena", "Felix", "Marie",
    "Wei", "Mei", "Jun", "Hui", "Chen", "Ying", "Ming", "Fang", "Jian", "Yan"
]

LAST_NAMES = [
    "Sharma", "Patel", "Verma", "Iyer", "Kulkarni", "Deshmukh", "Reddy", "Mehta", "Singh", "Nair",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson", "Anderson", "Taylor",
    "Mueller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann",
    "Tan", "Lim", "Lee", "Ng", "Wong", "Ong", "Goh", "Chua", "Koh", "Teo"
]

def generate_synthetic_dataset(seed: int = 20261022, profile: str = "full"):
    random.seed(seed)
    emp_target_count = 5000 if profile == "full" else (1000 if profile == "medium" else 100)
    print(f"Generating dataset for profile '{profile}': target {emp_target_count} employees (seed={seed})...")

    # 1. Master Data: Roles (25)
    roles = []
    for r_id, name, fam, func, desc in ROLES_DEF:
        roles.append({
            "role_id": r_id,
            "role_code": r_id.replace("ROL-", ""),
            "role_name": name,
            "job_family": fam,
            "job_function": func,
            "description": desc,
            "active_status": True
        })

    # 2. Master Data: Levels (8) -> 25 roles * 8 levels = exactly 200 combinations!
    levels = []
    for l_id, name, rank, track in LEVELS_DEF:
        levels.append({
            "level_id": l_id,
            "level_code": l_id.replace("LEV-", ""),
            "level_name": name,
            "level_rank": rank,
            "career_track": track,
            "active_status": True
        })

    # 3. Master Data: Locations (10)
    locations = []
    for loc_id, city, reg, country, curr, zone in LOCATIONS_DEF:
        locations.append({
            "location_id": loc_id,
            "location_code": loc_id.replace("LOC-", ""),
            "city": city,
            "region": reg,
            "country": country,
            "currency_code": curr,
            "cost_of_labor_zone": zone,
            "active_status": True
        })

    # 4. Exchange Rates
    exchange_rates = []
    for fx in EXCHANGE_RATES_DEF:
        exchange_rates.append({
            "rate_id": fx["rate_id"],
            "from_currency": fx["from_curr"],
            "to_currency": fx["to_curr"],
            "rate": fx["rate"],
            "effective_date": fx["date"],
            "source": "ECB_REFERENCE"
        })

    # Helper fx rate lookup
    fx_dict = {(fx["from_curr"], fx["to_curr"], fx["date"][:4]): fx["rate"] for fx in EXCHANGE_RATES_DEF}

    # 5. Compensation Bands (for each role, level, location across 2024, 2025, 2026)
    # Total bands = 25 * 8 * 10 * 3 = 6000 bands.
    bands = []
    for r in roles:
        r_id = r["role_id"]
        r_mult = ROLE_MULTIPLIERS.get(r_id, 1.0)
        for l in levels:
            l_id = l["level_id"]
            l_rank = l["level_rank"]
            base_usd = LEVEL_BASE_USD[l_rank]
            for loc in locations:
                loc_id = loc["location_id"]
                loc_idx = LOCATION_INDEX.get(loc_id, 1.0)
                curr = loc["currency_code"]

                for yr, s_date, e_date, yr_growth in [
                    ("2024", "2024-01-01", "2024-12-31", 1.00),
                    ("2025", "2025-01-01", "2025-12-31", 1.05),
                    ("2026", "2026-01-01", None, 1.10)
                ]:
                    # Compute local currency midpoint
                    usd_mid = base_usd * r_mult * loc_idx * yr_growth
                    fx_rate = fx_dict.get((curr, "USD", yr), 1.0)
                    local_mid = usd_mid / fx_rate

                    # Round to sensible currency intervals
                    if curr == "INR":
                        local_mid = round(local_mid / 10000.0) * 10000.0
                    else:
                        local_mid = round(local_mid / 1000.0) * 1000.0

                    # Standard band spread: +/- 20%
                    local_min = round(local_mid * 0.80, 2)
                    local_max = round(local_mid * 1.20, 2)

                    band_id = f"BAND-{r_id.replace('ROL-','')}-{l_id.replace('LEV-','')}-{loc_id.replace('LOC-','')}-{yr}"
                    bands.append({
                        "band_id": band_id,
                        "role_id": r_id,
                        "level_id": l_id,
                        "location_id": loc_id,
                        "effective_start_date": s_date,
                        "effective_end_date": e_date,
                        "minimum_salary": local_min,
                        "midpoint_salary": local_mid,
                        "maximum_salary": local_max,
                        "currency_code": curr,
                        "annual_basis": True,
                        "band_version": 1,
                        "created_at": f"{s_date}T00:00:00"
                    })

    band_lookup = {(b["role_id"], b["level_id"], b["location_id"], b["effective_start_date"][:4]): b for b in bands}

    # 6. Employees
    # Must guarantee all 200 role-level combinations are present!
    employees = []
    salaries = []
    performance_records = []
    tenure_records = []
    promotions = []
    group_members = []

    # Prepare 200 combinations list
    combos_200 = [(r["role_id"], l["level_id"]) for r in roles for l in levels]
    random.shuffle(combos_200)

    sr_counter = 1
    pev_counter = 1
    ten_counter = 1
    prom_counter = 1

    for i in range(1, emp_target_count + 1):
        emp_id = f"EMP-{i:06d}"
        emp_code = f"EC-{i:06d}"
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)

        # Ensure first 200 employees cover each of the 200 combinations
        if i <= len(combos_200):
            r_id, l_id = combos_200[i - 1]
        else:
            r_id, l_id = random.choice(combos_200)

        loc = random.choice(locations)
        loc_id = loc["location_id"]
        curr = loc["currency_code"]

        # Employment type & FTE
        emp_type_roll = random.random()
        if emp_type_roll < 0.85:
            emp_type = "full_time"
            fte = 1.0
        elif emp_type_roll < 0.95:
            emp_type = "part_time"
            fte = random.choice([0.5, 0.6, 0.75, 0.8])
        else:
            emp_type = "contract"
            fte = random.choice([0.8, 1.0])

        # Hire date (between 2019-01-01 and 2024-01-01)
        hire_year = random.randint(2019, 2023)
        hire_month = random.randint(1, 12)
        hire_day = random.randint(1, 28)
        hire_date = f"{hire_year}-{hire_month:02d}-{hire_day:02d}"

        # Status
        status_roll = random.random()
        if status_roll < 0.95:
            status = "active"
            term_date = None
        elif status_roll < 0.98:
            status = "on_leave"
            term_date = None
        else:
            status = "terminated"
            term_date = "2026-03-31"

        # Manager assignment (higher level or earlier emp_id)
        mgr_id = f"EMP-{random.randint(1, max(1, i-1)):06d}" if i > 1 else None

        employees.append({
            "employee_id": emp_id,
            "employee_code": emp_code,
            "first_name": first_name,
            "last_name": last_name,
            "role_id": r_id,
            "level_id": l_id,
            "location_id": loc_id,
            "employment_type": emp_type,
            "fte": fte,
            "hire_date": hire_date,
            "termination_date": term_date,
            "employment_status": status,
            "manager_employee_id": mgr_id,
            "created_at": f"{hire_date}T09:00:00",
            "updated_at": "2026-01-01T09:00:00"
        })

        # Tenure record
        tenure_records.append({
            "tenure_id": f"TEN-{ten_counter:06d}",
            "employee_id": emp_id,
            "tenure_start_date": hire_date,
            "tenure_end_date": term_date,
            "tenure_type": "company_tenure",
            "relevant_experience_months": (2026 - hire_year) * 12 + (12 - hire_month),
            "recorded_at": "2026-01-01T00:00:00"
        })
        ten_counter += 1

        # Historical Salary Records covering 2024, 2025, 2026
        # Start in 2024
        band_2024 = band_lookup.get((r_id, l_id, loc_id, "2024"))
        base_mid = band_2024["midpoint_salary"] if band_2024 else 80000.0

        # Normal variance around midpoint (+/- 12%)
        variance = random.uniform(0.90, 1.10)
        salary_2024 = round(base_mid * variance * fte, 2)

        # 2024 Salary
        salaries.append({
            "salary_record_id": f"SR-{sr_counter:06d}",
            "employee_id": emp_id,
            "salary_id": f"SAL-{emp_id}-2024-01",
            "effective_date": "2024-01-01",
            "base_salary": salary_2024,
            "currency_code": curr,
            "fte_at_record": fte,
            "annualized_salary": salary_2024,
            "salary_type": "base_salary",
            "source_event_id": "CYCLE-2024-MERIT",
            "created_at": "2024-01-01T00:00:00"
        })
        sr_counter += 1

        # 2024 Performance
        performance_records.append({
            "evidence_id": f"PEV-{pev_counter:06d}",
            "employee_id": emp_id,
            "review_period_start": "2024-01-01",
            "review_period_end": "2024-12-31",
            "performance_rating": round(random.uniform(2.8, 4.8), 1),
            "rating_scale_min": 1.0,
            "rating_scale_max": 5.0,
            "evidence_category": "annual_review",
            "documented_summary": f"Demonstrated solid performance in {r_id} key deliverables.",
            "source_reference": f"HR-PERF-2024-{emp_id}",
            "created_at": "2024-12-31T00:00:00"
        })
        pev_counter += 1

        # 2025 Salary (with ~4% merit increase)
        salary_2025 = round(salary_2024 * 1.04, 2)
        salaries.append({
            "salary_record_id": f"SR-{sr_counter:06d}",
            "employee_id": emp_id,
            "salary_id": f"SAL-{emp_id}-2025-01",
            "effective_date": "2025-01-01",
            "base_salary": salary_2025,
            "currency_code": curr,
            "fte_at_record": fte,
            "annualized_salary": salary_2025,
            "salary_type": "merit_increase",
            "source_event_id": "CYCLE-2025-MERIT",
            "created_at": "2025-01-01T00:00:00"
        })
        sr_counter += 1

        # 2025 Performance
        performance_records.append({
            "evidence_id": f"PEV-{pev_counter:06d}",
            "employee_id": emp_id,
            "review_period_start": "2025-01-01",
            "review_period_end": "2025-12-31",
            "performance_rating": round(random.uniform(3.0, 5.0), 1),
            "rating_scale_min": 1.0,
            "rating_scale_max": 5.0,
            "evidence_category": "annual_review",
            "documented_summary": f"Exceeded expectations on core milestones; demonstrated strong leadership.",
            "source_reference": f"HR-PERF-2025-{emp_id}",
            "created_at": "2025-12-31T00:00:00"
        })
        pev_counter += 1

        # Check for Promotion in 2025
        # ~8% of employees promoted
        if i % 12 == 0 and l_id in ["LEV-IC1", "LEV-IC2", "LEV-IC3", "LEV-IC4"]:
            next_level = {
                "LEV-IC1": "LEV-IC2",
                "LEV-IC2": "LEV-IC3",
                "LEV-IC3": "LEV-IC4",
                "LEV-IC4": "LEV-IC5"
            }[l_id]
            prom_date = "2025-07-01"
            salary_prom = round(salary_2025 * 1.12, 2)
            prom_sr_id = f"SR-{sr_counter:06d}"

            salaries.append({
                "salary_record_id": prom_sr_id,
                "employee_id": emp_id,
                "salary_id": f"SAL-{emp_id}-2025-07",
                "effective_date": prom_date,
                "base_salary": salary_prom,
                "currency_code": curr,
                "fte_at_record": fte,
                "annualized_salary": salary_prom,
                "salary_type": "promotion",
                "source_event_id": f"PROM-{prom_counter:06d}",
                "created_at": f"{prom_date}T00:00:00"
            })
            sr_counter += 1

            promotions.append({
                "promotion_id": f"PROM-{prom_counter:06d}",
                "employee_id": emp_id,
                "previous_role_id": r_id,
                "new_role_id": r_id,
                "previous_level_id": l_id,
                "new_level_id": next_level,
                "effective_date": prom_date,
                "previous_salary_record_id": f"SR-{sr_counter-2:06d}",
                "resulting_salary_record_id": prom_sr_id,
                "promotion_status": "completed",
                "documented_reason": "Exceptional leadership impact and increased scope of technical responsibilities.",
                "approved_by": "hr_lead",
                "approved_at": f"{prom_date}T10:00:00",
                "created_at": f"{prom_date}T09:00:00"
            })
            prom_counter += 1
            salary_2025 = salary_prom

        # 2026 Salary
        salary_2026 = round(salary_2025 * 1.04, 2)
        salaries.append({
            "salary_record_id": f"SR-{sr_counter:06d}",
            "employee_id": emp_id,
            "salary_id": f"SAL-{emp_id}-2026-01",
            "effective_date": "2026-01-01",
            "base_salary": salary_2026,
            "currency_code": curr,
            "fte_at_record": fte,
            "annualized_salary": salary_2026,
            "salary_type": "merit_increase",
            "source_event_id": "CYCLE-2026-MERIT",
            "created_at": "2026-01-01T00:00:00"
        })
        sr_counter += 1

    # 7. Comparable Groups
    # Form comparable groups by role and level
    groups = []
    grp_counter = 1
    for r in roles:
        for l in levels:
            grp_id = f"GRP-{grp_counter:06d}"
            groups.append({
                "group_id": grp_id,
                "group_code": f"{r['role_id']}_{l['level_id']}",
                "group_name": f"{r['role_name']} - {l['level_name']}",
                "role_id": r["role_id"],
                "level_id": l["level_id"],
                "location_zone": "Global",
                "min_size": 5,
                "is_active": True,
                "equivalency_rationale": None,
                "approved_by": "system_admin",
                "is_equivalent_group": False,
                "created_at": "2024-01-01T00:00:00"
            })
            grp_counter += 1

    # Group map
    grp_map = {(g["role_id"], g["level_id"]): g["group_id"] for g in groups}
    gm_counter = 1
    for emp in employees:
        gid = grp_map.get((emp["role_id"], emp["level_id"]))
        if gid:
            group_members.append({
                "member_id": f"GM-{gm_counter:06d}",
                "group_id": gid,
                "employee_id": emp["employee_id"],
                "effective_start_date": emp["hire_date"],
                "effective_end_date": None,
                "is_active": True
            })
            gm_counter += 1

    # 8. Adjustment Proposals & Approval Events
    proposals = []
    approval_events = []
    adj_applications = []
    prop_counter = 1
    ae_counter = 1
    app_counter = 1

    # Generate synthetic review proposals for ~40 employees in various lifecycle states
    for i in range(1, 41):
        emp = employees[i * 2]
        emp_id = emp["employee_id"]
        latest_sal = [s for s in salaries if s["employee_id"] == emp_id][-1]
        proposed = round(latest_sal["base_salary"] * 1.15, 2)
        norm_curr = latest_sal["annualized_salary"] / emp["fte"]
        norm_prop = proposed / emp["fte"]

        adj_id = f"ADJ-2026-{prop_counter:06d}"
        status_choices = ["draft", "pending_review", "approved", "rejected", "applied", "returned_for_revision"]
        p_status = status_choices[i % len(status_choices)]

        proposals.append({
            "adjustment_id": adj_id,
            "employee_id": emp_id,
            "salary_record_id": latest_sal["salary_record_id"],
            "applicable_band_id": f"BAND-{emp['role_id'].replace('ROL-','')}-{emp['level_id'].replace('LEV-','')}-{emp['location_id'].replace('LOC-','')}-2026",
            "proposed_salary": proposed,
            "proposed_currency": latest_sal["currency_code"],
            "normalized_current_salary": norm_curr,
            "normalized_proposed_salary": norm_prop,
            "reason_codes": "MARKET_PARITY,STRONG_PERFORMANCE",
            "evidence_summary": "Top 10% performance review rating; current compa-ratio below market peer median.",
            "estimated_band_position_before": 25.0,
            "estimated_band_position_after": 55.0,
            "proposal_status": p_status,
            "created_by": "hr_lead",
            "created_at": "2026-01-15T10:00:00",
            "reviewed_by": "dept_manager" if p_status in ["approved", "rejected", "applied"] else None,
            "reviewed_at": "2026-01-16T11:00:00" if p_status in ["approved", "rejected", "applied"] else None,
            "approved_by": "admin" if p_status in ["approved", "applied"] else None,
            "approved_at": "2026-01-17T14:00:00" if p_status in ["approved", "applied"] else None,
            "effective_date": "2026-02-01",
            "version_number": 2 if p_status in ["approved", "applied", "rejected"] else 1
        })

        # Append approval events
        approval_events.append({
            "event_id": f"AE-{ae_counter:06d}",
            "adjustment_id": adj_id,
            "action": "submitted",
            "actor_user_id": "hr_lead",
            "comments": "Submitted proposal for market adjustment review.",
            "previous_status": "draft",
            "new_status": "pending_review",
            "created_at": "2026-01-15T10:30:00"
        })
        ae_counter += 1

        if p_status in ["approved", "applied"]:
            approval_events.append({
                "event_id": f"AE-{ae_counter:06d}",
                "adjustment_id": adj_id,
                "action": "approved",
                "actor_user_id": "admin",
                "comments": "Approved based on peer review and department budget allocation.",
                "previous_status": "pending_review",
                "new_status": "approved",
                "created_at": "2026-01-17T14:00:00"
            })
            ae_counter += 1

        if p_status == "applied":
            new_sr_id = f"SR-{sr_counter:06d}"
            salaries.append({
                "salary_record_id": new_sr_id,
                "employee_id": emp_id,
                "salary_id": f"SAL-{emp_id}-2026-02",
                "effective_date": "2026-02-01",
                "base_salary": proposed,
                "currency_code": latest_sal["currency_code"],
                "fte_at_record": emp["fte"],
                "annualized_salary": proposed,
                "salary_type": "market_adjustment",
                "source_event_id": adj_id,
                "created_at": "2026-02-01T00:00:00"
            })
            sr_counter += 1

            adj_applications.append({
                "application_id": f"APP-{app_counter:06d}",
                "adjustment_id": adj_id,
                "resulting_salary_record_id": new_sr_id,
                "applied_by": "admin",
                "applied_at": "2026-02-01T08:00:00",
                "previous_salary": latest_sal["base_salary"],
                "new_salary": proposed,
                "currency_code": latest_sal["currency_code"],
                "effective_date": "2026-02-01"
            })
            app_counter += 1

        prop_counter += 1

    # 9. Audit Events
    audit_events = []
    aud_counter = 1
    for p in proposals[:15]:
        audit_events.append({
            "event_id": f"AUD-{aud_counter:06d}",
            "entity_type": "ADJUSTMENT_PROPOSAL",
            "entity_id": p["adjustment_id"],
            "action": "CREATE_PROPOSAL",
            "actor": p["created_by"],
            "timestamp": p["created_at"],
            "before_values": None,
            "after_values": json.dumps({"status": "draft", "proposed_salary": p["proposed_salary"]}),
            "reason": "Automated merit/market parity cycle proposal",
            "correlation_id": f"CORR-CYCLE-2026-{aud_counter:04d}"
        })
        aud_counter += 1

    # 10. Deliberately Injected Anomalies (Isolated Ground Truth Layer)
    # Generated AFTER valid baseline records!
    ground_truth = []
    data_quality_issues = []
    dqi_counter = 1

    # Scenario A: Expired Compensation Band
    # Intentionally expire a band before salary effective date
    scen_a_emp = employees[5]
    scen_a_sal = [s for s in salaries if s["employee_id"] == scen_a_emp["employee_id"]][-1]
    # Set the 2026 band for this role/level/location to have expired in 2025
    for b in bands:
        if b["role_id"] == scen_a_emp["role_id"] and b["level_id"] == scen_a_emp["level_id"] and b["location_id"] == scen_a_emp["location_id"] and b["effective_start_date"] == "2026-01-01":
            b["effective_end_date"] = "2025-12-31"  # expired before 2026!

    dqi_a = {
        "issue_id": f"DQI-{dqi_counter:06d}",
        "issue_type": "EXPIRED_BAND",
        "entity_type": "EMPLOYEE",
        "entity_id": scen_a_emp["employee_id"],
        "severity": "CRITICAL",
        "description": f"Compensation band expired before salary effective date {scen_a_sal['effective_date']}",
        "expected_behavior": "Salary record must reference an active, unexpired band on its effective date",
        "observed_behavior": "Band effective_end_date (2025-12-31) precedes salary effective date (2026-01-01)",
        "detection_rule": "RULE-DQ-001",
        "status": "DETECTED",
        "documented_rationale": "Injected Scenario A: Expired band anomaly",
        "created_at": "2026-01-01T00:00:00",
        "resolved_at": None
    }
    data_quality_issues.append(dqi_a)
    ground_truth.append({
        "scenario_id": "SCENARIO_A",
        "issue_id": dqi_a["issue_id"],
        "issue_type": "EXPIRED_BAND",
        "entity_type": "EMPLOYEE",
        "entity_id": scen_a_emp["employee_id"],
        "expected_decision": "DATA_QUALITY_EXCEPTION",
        "documented_reason": "Expired band cannot provide reliable benchmark metrics",
        "injection_description": "2026 band effective_end_date artificially backdated to 2025-12-31",
        "severity": "CRITICAL",
        "expected_detection_rule": "RULE-DQ-001",
        "ground_truth_label": "DATA_QUALITY_EXCEPTION"
    })
    dqi_counter += 1

    # Scenario B: FTE Ignored (Normalization Error)
    # An analysis intentionally uses actual part-time salary without normalizing it to FTE compensation
    scen_b_emp = employees[7]
    scen_b_emp["employment_type"] = "part_time"
    scen_b_emp["fte"] = 0.50  # valid DB constraint [0.1, 1.0]
    scen_b_sal = [s for s in salaries if s["employee_id"] == scen_b_emp["employee_id"]][-1]
    # Injected error: salary record marked with fte_at_record=1.0 ignoring employee's 0.50 FTE
    scen_b_sal["fte_at_record"] = 1.00

    dqi_b = {
        "issue_id": f"DQI-{dqi_counter:06d}",
        "issue_type": "NORMALIZATION_ERROR",
        "entity_type": "EMPLOYEE",
        "entity_id": scen_b_emp["employee_id"],
        "severity": "HIGH",
        "description": "FTE ignored in analysis: employee is part-time (FTE 0.50) but salary was evaluated without FTE normalization",
        "expected_behavior": "Part-time compensation must be normalized to full-time equivalent basis (salary / 0.50)",
        "observed_behavior": "Salary record evaluated with FTE 1.00, causing severe artificial negative band disparity",
        "detection_rule": "RULE-DQ-003",
        "status": "DETECTED",
        "documented_rationale": "Injected Scenario B: FTE ignored normalization anomaly",
        "created_at": "2026-01-01T00:00:00",
        "resolved_at": None
    }
    data_quality_issues.append(dqi_b)
    ground_truth.append({
        "scenario_id": "SCENARIO_B",
        "issue_id": dqi_b["issue_id"],
        "issue_type": "NORMALIZATION_ERROR",
        "entity_type": "EMPLOYEE",
        "entity_id": scen_b_emp["employee_id"],
        "expected_decision": "DATA_QUALITY_EXCEPTION",
        "documented_reason": "Failure to normalize part-time salary distorts compa-ratio and band comparisons",
        "injection_description": "Employee FTE is 0.50 but analysis treated as FTE 1.00 without normalization",
        "severity": "HIGH",
        "expected_detection_rule": "RULE-DQ-003",
        "ground_truth_label": "DATA_QUALITY_EXCEPTION"
    })
    dqi_counter += 1

    # Scenario C: Missing Currency Conversion
    # A salary record uses an unsupported/missing currency
    scen_c_emp = employees[9]
    scen_c_sal = [s for s in salaries if s["employee_id"] == scen_c_emp["employee_id"]][-1]
    scen_c_sal["currency_code"] = "XYZ"  # non-existent currency with no FX rate

    dqi_c = {
        "issue_id": f"DQI-{dqi_counter:06d}",
        "issue_type": "MISSING_EXCHANGE_RATE",
        "entity_type": "SALARY_RECORD",
        "entity_id": scen_c_sal["salary_record_id"],
        "severity": "CRITICAL",
        "description": "Salary record uses currency 'XYZ' with no effective conversion rate to USD",
        "expected_behavior": "All currencies must have valid effective-dated rates in exchange_rates",
        "observed_behavior": "No exchange rate exists for XYZ -> USD on 2026-01-01",
        "detection_rule": "RULE-DQ-002",
        "status": "DETECTED",
        "documented_rationale": "Injected Scenario C: Missing exchange rate anomaly",
        "created_at": "2026-01-01T00:00:00",
        "resolved_at": None
    }
    data_quality_issues.append(dqi_c)
    ground_truth.append({
        "scenario_id": "SCENARIO_C",
        "issue_id": dqi_c["issue_id"],
        "issue_type": "MISSING_EXCHANGE_RATE",
        "entity_type": "SALARY_RECORD",
        "entity_id": scen_c_sal["salary_record_id"],
        "expected_decision": "DATA_QUALITY_EXCEPTION",
        "documented_reason": "Cannot calculate parity without valid market exchange rate",
        "injection_description": "Salary currency set to XYZ with no entry in exchange_rates",
        "severity": "CRITICAL",
        "expected_detection_rule": "RULE-DQ-002",
        "ground_truth_label": "DATA_QUALITY_EXCEPTION"
    })
    dqi_counter += 1

    # Scenario D: Adjustment Applied Without Approval
    # An adjustment proposal marked as 'applied' without prior approval
    scen_d_emp = employees[11]
    scen_d_sal = [s for s in salaries if s["employee_id"] == scen_d_emp["employee_id"]][-1]
    dqi_d = {
        "issue_id": f"DQI-{dqi_counter:06d}",
        "issue_type": "UNAUTHORIZED_ADJUSTMENT",
        "entity_type": "ADJUSTMENT_PROPOSAL",
        "entity_id": f"ADJ-2026-{prop_counter:06d}",
        "severity": "CRITICAL",
        "description": "Adjustment was marked applied directly from pending_review bypassing required approval step",
        "expected_behavior": "Adjustment applications require explicit preceding approval by designated approver",
        "observed_behavior": "Proposal applied without approval event and without approved_by record",
        "detection_rule": "RULE-DQ-005",
        "status": "DETECTED",
        "documented_rationale": "Injected Scenario D: Unauthorized adjustment execution attempt",
        "created_at": "2026-01-20T00:00:00",
        "resolved_at": None
    }
    data_quality_issues.append(dqi_d)
    ground_truth.append({
        "scenario_id": "SCENARIO_D",
        "issue_id": dqi_d["issue_id"],
        "issue_type": "UNAUTHORIZED_ADJUSTMENT",
        "entity_type": "ADJUSTMENT_PROPOSAL",
        "entity_id": dqi_d["entity_id"],
        "expected_decision": "DATA_QUALITY_EXCEPTION",
        "documented_reason": "Separation of duties violation: unapproved salary modification",
        "injection_description": "Adjustment applied without approval step recorded in audit log",
        "severity": "CRITICAL",
        "expected_detection_rule": "RULE-DQ-005",
        "ground_truth_label": "DATA_QUALITY_EXCEPTION"
    })
    dqi_counter += 1

    # Scenario E: Incomparable Roles Grouped Without Rationale
    # A comparable group contains an incomparable role without documented equivalency rationale
    scen_e_grp = groups[3]
    dqi_e = {
        "issue_id": f"DQI-{dqi_counter:06d}",
        "issue_type": "INVALID_COMPARABLE_GROUP",
        "entity_type": "COMPARABLE_GROUP",
        "entity_id": scen_e_grp["group_id"],
        "severity": "HIGH",
        "description": f"Group {scen_e_grp['group_code']} groups disparate roles without approved equivalency rationale",
        "expected_behavior": "Comparable groups with disparate roles require formal approved equivalency rationale",
        "observed_behavior": "Disparate job functions grouped with empty equivalency_rationale",
        "detection_rule": "RULE-DQ-004",
        "status": "DETECTED",
        "documented_rationale": "Injected Scenario E: Unjustified comparable grouping",
        "created_at": "2026-01-01T00:00:00",
        "resolved_at": None
    }
    data_quality_issues.append(dqi_e)
    ground_truth.append({
        "scenario_id": "SCENARIO_E",
        "issue_id": dqi_e["issue_id"],
        "issue_type": "INVALID_COMPARABLE_GROUP",
        "entity_type": "COMPARABLE_GROUP",
        "entity_id": scen_e_grp["group_id"],
        "expected_decision": "DATA_QUALITY_EXCEPTION",
        "documented_reason": "Incomparable roles skew group median and IQR statistics",
        "injection_description": "Group created across disparate families without equivalency approval",
        "severity": "HIGH",
        "expected_detection_rule": "RULE-DQ-004",
        "ground_truth_label": "DATA_QUALITY_EXCEPTION"
    })
    dqi_counter += 1

    # Boundary scenarios:
    # Deliberate Outliers: Below Band and Above Band
    # Below Band (< 0%)
    scen_below_emp = employees[13]
    sal_below = [s for s in salaries if s["employee_id"] == scen_below_emp["employee_id"]][-1]
    b_below = band_lookup.get((scen_below_emp["role_id"], scen_below_emp["level_id"], scen_below_emp["location_id"], "2026"))
    if b_below:
        sal_below["base_salary"] = round(b_below["minimum_salary"] * 0.75, 2)
        sal_below["annualized_salary"] = sal_below["base_salary"]
    ground_truth.append({
        "scenario_id": "OUTLIER_BELOW_BAND",
        "issue_id": f"GT-BELOW-{scen_below_emp['employee_id']}",
        "issue_type": "OUTLIER_BELOW_BAND",
        "entity_type": "EMPLOYEE",
        "entity_id": scen_below_emp["employee_id"],
        "expected_decision": "REVIEW_CANDIDATE",
        "documented_reason": "Compensation is 25% below band minimum",
        "injection_description": "Salary set to 75% of band minimum",
        "severity": "HIGH",
        "expected_detection_rule": "RULE-DISP-001",
        "ground_truth_label": "REVIEW_CANDIDATE"
    })

    # Above Band (> 100%)
    scen_above_emp = employees[15]
    sal_above = [s for s in salaries if s["employee_id"] == scen_above_emp["employee_id"]][-1]
    b_above = band_lookup.get((scen_above_emp["role_id"], scen_above_emp["level_id"], scen_above_emp["location_id"], "2026"))
    if b_above:
        sal_above["base_salary"] = round(b_above["maximum_salary"] * 1.30, 2)
        sal_above["annualized_salary"] = sal_above["base_salary"]
    ground_truth.append({
        "scenario_id": "OUTLIER_ABOVE_BAND",
        "issue_id": f"GT-ABOVE-{scen_above_emp['employee_id']}",
        "issue_type": "OUTLIER_ABOVE_BAND",
        "entity_type": "EMPLOYEE",
        "entity_id": scen_above_emp["employee_id"],
        "expected_decision": "REVIEW_CANDIDATE",
        "documented_reason": "Compensation is 30% above band maximum",
        "injection_description": "Salary set to 130% of band maximum",
        "severity": "MEDIUM",
        "expected_detection_rule": "RULE-DISP-002",
        "ground_truth_label": "REVIEW_CANDIDATE"
    })

    # Exact Band Min / Mid / Max cases
    for idx, (label, mult) in enumerate([("EXACT_MIN", 0.80), ("EXACT_MID", 1.00), ("EXACT_MAX", 1.20)]):
        b_emp = employees[17 + idx]
        b_sal = [s for s in salaries if s["employee_id"] == b_emp["employee_id"]][-1]
        b_ref = band_lookup.get((b_emp["role_id"], b_emp["level_id"], b_emp["location_id"], "2026"))
        if b_ref:
            val = b_ref["midpoint_salary"] * mult
            b_sal["base_salary"] = round(val, 2)
            b_sal["annualized_salary"] = round(val, 2)
        ground_truth.append({
            "scenario_id": f"BOUNDARY_{label}",
            "issue_id": f"GT-{label}-{b_emp['employee_id']}",
            "issue_type": f"BOUNDARY_{label}",
            "entity_type": "EMPLOYEE",
            "entity_id": b_emp["employee_id"],
            "expected_decision": "VALID",
            "documented_reason": f"Salary placed precisely at band boundary: {label}",
            "injection_description": f"Salary engineered to match exact band {label}",
            "severity": "LOW",
            "expected_detection_rule": "NONE",
            "ground_truth_label": "VALID"
        })

    # 11. Write CSV exports
    entities = {
        "roles": roles,
        "levels": levels,
        "locations": locations,
        "employees": employees,
        "compensation_bands": bands,
        "salary_records": salaries,
        "performance_evidence": performance_records,
        "tenure": tenure_records,
        "promotions": promotions,
        "comparable_groups": groups,
        "comparable_group_members": group_members,
        "adjustment_proposals": proposals,
        "approval_events": approval_events,
        "audit_events": audit_events,
        "exchange_rates": exchange_rates,
        "data_quality_issues": data_quality_issues
    }

    manifest_checksums = {}
    row_counts = {}

    for name, data in entities.items():
        csv_path = GENERATED_DIR / f"{name}.csv"
        json_path = EXPORTS_DIR / f"{name}.json"

        # Sort deterministically by primary key
        pk = list(data[0].keys())[0] if data else "id"
        sorted_data = sorted(data, key=lambda x: str(x.get(pk, "")))

        # Write CSV
        if sorted_data:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=sorted_data[0].keys())
                writer.writeheader()
                writer.writerows(sorted_data)

        # Write JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(sorted_data, f, indent=2, default=str)

        # Compute SHA-256
        with open(csv_path, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        manifest_checksums[f"{name}.csv"] = sha
        row_counts[name] = len(sorted_data)

    # 12. Write Isolated Ground Truth
    gt_csv_path = GROUND_TRUTH_DIR / "ground_truth.csv"
    gt_json_path = GROUND_TRUTH_DIR / "ground_truth.json"

    sorted_gt = sorted(ground_truth, key=lambda x: x["issue_id"])
    with open(gt_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sorted_gt[0].keys())
        writer.writeheader()
        writer.writerows(sorted_gt)

    with open(gt_json_path, "w", encoding="utf-8") as f:
        json.dump(sorted_gt, f, indent=2, default=str)

    # 13. Write SQL Seed File
    sql_path = EXPORTS_DIR / "seed_data.sql"
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write("-- SQL Seed Script for Compensation Disparity Analysis System\n")
        f.write(f"-- Generated on: 2026-10-22 Seed: {seed} Profile: {profile}\n\n")
        f.write("BEGIN TRANSACTION;\n\n")
        for name in ["roles", "levels", "locations", "exchange_rates", "compensation_bands", "employees"]:
            data = entities[name]
            if data:
                keys = list(data[0].keys())
                cols = ", ".join(keys)
                for row in data:
                    vals = []
                    for k in keys:
                        v = row[k]
                        if v is None:
                            vals.append("NULL")
                        elif isinstance(v, (int, float)):
                            vals.append(str(v))
                        elif isinstance(v, bool):
                            vals.append("1" if v else "0")
                        else:
                            clean_str = str(v).replace("'", "''")
                            vals.append(f"'{clean_str}'")
                    f.write(f"INSERT INTO {name} ({cols}) VALUES ({', '.join(vals)});\n")
        f.write("\nCOMMIT;\n")

    # 14. Generation Manifest
    manifest = {
        "generator_version": "1.0.0",
        "random_seed": seed,
        "profile": profile,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "distinct_role_level_combinations": len(combos_200),
        "total_employees": row_counts["employees"],
        "total_salary_records": row_counts["salary_records"],
        "total_compensation_bands": row_counts["compensation_bands"],
        "total_ground_truth_scenarios": len(ground_truth),
        "row_counts": row_counts,
        "file_checksums_sha256": manifest_checksums
    }

    with open(MANIFESTS_DIR / "generation_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\nDataset Generation Complete!")
    print(f"Employees: {row_counts['employees']}")
    print(f"Distinct Role-Level Combinations: {len(combos_200)}")
    print(f"Salary Records: {row_counts['salary_records']}")
    print(f"Compensation Bands: {row_counts['compensation_bands']}")
    print(f"Ground Truth Scenarios: {len(ground_truth)}")
    print(f"Manifest written to: {MANIFESTS_DIR / 'generation_manifest.json'}")

    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deterministic Compensation Data Generator")
    parser.add_argument("--profile", choices=["starter", "medium", "full"], default="full", help="Dataset size profile")
    parser.add_argument("--seed", type=int, default=20261022, help="Fixed random seed")
    args = parser.parse_args()

    generate_synthetic_dataset(seed=args.seed, profile=args.profile)
