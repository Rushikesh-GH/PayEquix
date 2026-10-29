# PayEquix: Compensation Disparity Analysis & Explainable Pay Equity Review System

[![Public GitHub Repository](https://img.shields.io/badge/GitHub-Rushikesh--GH%2FPayEquix-blue?logo=github)](https://github.com/Rushikesh-GH/PayEquix)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3.1-61dafb.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38bdf8.svg)](https://tailwindcss.com/)
[![Validation](https://img.shields.io/badge/Validation-22%2F22%20PASS-emerald.svg)](docs/validation_report.md)
[![Evaluation F1](https://img.shields.io/badge/Evaluation%20F1-1.0000-brightgreen.svg)](docs/evaluation_report.md)
[![Reproducibility](https://img.shields.io/badge/Determinism-100%25%20Bitwise-success.svg)](scripts/check_reproducibility.py)

> [!NOTE]
> ### 👤 Project Ownership & Contributor Clarification
> - **Sole Project Author & Developer:** **`Rushikesh-GH`** ([rushidivekar21@gmail.com](mailto:rushidivekar21@gmail.com))
> - **Notice Regarding Secondary Contributor Profile:** The local Windows development machine previously had a legacy global Git configuration under `PratikDivekar4211`. All architecture, engineering, data generation, backend services, 3D WebGL visualizations, and test validations are the **exclusive individual work of Rushikesh-GH**. The second handle appeared only as a default local environment artifact and holds no commits or code contributions.
> - **Adherence to Recruitment Guidelines:** Confirms 100% individual authorship as stipulated in the YottaFlex AI Candidate Project Guidelines.

---

## 1. Business Problem & Ethical Guardrails

Modern multinational enterprises require defensible, explainable mechanisms to evaluate compensation across roles, career levels, geographic cost-of-labor zones, work hours, and effective-dated market bands.

### Key Non-Adverse Principles & Guardrails:
1. **Statistical Signals Are Investigation Prompts, Not Proof of Wrongdoing:** Statistical disparity flags indicate candidates for documented human review, never an automatic declaration of discrimination.
2. **Strict Exclusion of Protected Attributes:** Demographic protected characteristics (gender, race, age, religion) are **never** utilized as features in compensation models or individual adjustment proposals.
3. **Data Quality vs Review Candidate Separation:** Records corrupted by expired bands, unnormalized FTE, or missing FX rates are categorized as `DATA_QUALITY_EXCEPTION` rather than compensation disparity candidates.
4. **Dual-Custody Human Governance:** Proposals require dual approval; creators are prohibited from self-approving their own submissions.

---

## 2. Key Features & Skills Incorporated

- **Deterministic Synthetic Generation:** 5,000 employees, exactly 200 distinct role-level combinations, and 3-year historical salary records covering 2024, 2025, and 2026 with fixed seed `20261022`.
- **Reusable Compensation Normalization:**
  - Annualization: monthly base $\times$ 12 or annual amount directly.
  - Effective-dated currency conversion to USD reporting currency.
  - Full-Time Equivalent (FTE) normalization: $\text{Annualized} / \text{FTE}$.
  - Compa-Ratio ($\text{FTE Salary} / \text{Band Midpoint}$) and unclipped Within-Band Position ($\%$) preserving true outliers.
- **Rule-Based Disparity Engine:** Identifies below-band ($<0\%$), above-band ($>100\%$), severe midpoint disparities ($<0.80$), and peer group IQR outliers.
- **Human-in-the-Loop Proposal Lifecycle:**
  - `draft -> pending_review -> approved | rejected | returned_for_revision -> applied`
  - Optimistic locking, transactional application, creation of new immutable `SalaryRecord`, and audit logging.
- **Append-Only Audit Trail:** Captures every status change, before/after values, actor, timestamp, and correlation ID.
- **Isolated Ground Truth:** Negative scenarios (expired bands, FTE errors, missing FX, unauthorized adjustments, invalid groups) isolated from analytical feature inputs.
- **Agentic AI & Vector Database Copilot:**
  - Pinecone/Weaviate-style vector policy retrieval with cosine similarity embeddings (`/api/v1/ai/vector-search`).
  - Multi-agent collaboration pipeline (Disparity Analyst, Policy Compliance, and Proposal Synthesizer agents) with LLM observability telemetry (`/api/v1/ai/crew-triage/{id}`).
- **Interactive Full-App 3D Spatial Experience:**
  - Workforce Compensation Landscape Galaxy (WebGL Three.js).
  - Exception Triage Radar & Defect Scanner.
  - Salary Band Spatial Alignment Horizon Tunnel.
  - Multi-Cohort 3D Disparity Space.
  - Mouse-tracking 3D specular perspective tilt cards.
- **Cloud & Containerization:** Docker, Docker Compose, and step-by-step AWS deployment guides.

---

## 3. Technology Stack

- **Backend:** Python 3.10+, FastAPI, Pydantic v2, SQLAlchemy 2.0.
- **Database:** SQLite (local execution with `PRAGMA foreign_keys=ON;`), fully compatible with PostgreSQL.
- **Data Engineering:** pandas, NumPy.
- **Security:** PyJWT, bcrypt password hashing, Role-Based Access Control (RBAC).
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts, Three.js (WebGL).
- **AI / Vector Architecture:** Vector embedding simulation (Pinecone/Weaviate style), CrewAI / LangGraph multi-agent DAG patterns.
- **Testing:** pytest, FastAPI TestClient, 22-rule automated structural validation, isolated ground-truth metrics.
- **Deployment:** Docker, Docker Compose, AWS Cloud architecture.

---

## 4. Repository Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application & lifespan
│   │   ├── config.py            # Environment settings & thresholds
│   │   ├── database.py          # SQLAlchemy engine & session maker
│   │   ├── models/              # Relational models (Role, Level, Employee, etc.)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── api/                 # Versioned REST routers (/api/v1)
│   │   ├── analytics/           # Normalization & disparity detection engine
│   │   ├── audit/               # Append-only audit logging service
│   │   └── security/            # JWT authentication & RBAC middleware
│   ├── tests/                   # Automated unit and integration test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable components (Navbar, MetricCard, Badges)
│   │   ├── pages/               # Dashboard, Explorer, Detail, Exceptions, Proposals
│   │   ├── services/            # Axios/Fetch API client
│   │   └── types/               # TypeScript interfaces
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
├── data/
│   ├── generated/               # Deterministic CSV exports (roles, employees, etc.)
│   ├── ground_truth/            # Isolated ground truth labels (ground_truth.json)
│   ├── exports/                 # JSON exports & seed_data.sql
│   └── manifests/               # Generation & validation manifests with SHA-256
├── scripts/
│   ├── generate_data.py         # Deterministic data generator (seed 20261022)
│   ├── seed_database.py         # Database initializer & batch seeder
│   ├── validate_data.py         # 22-point structural validation suite
│   ├── calculate_metrics.py     # Evaluation against isolated ground truth
│   └── check_reproducibility.py # Bitwise reproducibility verification
├── docs/
│   ├── architecture.md          # Architecture & ERD diagrams
│   ├── data_dictionary.md       # Comprehensive entity schema dictionary
│   ├── business_rules.md        # Mathematical formulas & detection rules
│   ├── api_reference.md         # REST API documentation
│   ├── validation_report.md     # 22-point validation execution report
│   └── evaluation_report.md     # Precision, Recall, and F1 evaluation report
├── docker-compose.yml
├── Makefile
├── .env.example
├── .gitignore
└── README.md
```

---

## 5. Local Setup & Execution Instructions

### A. Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm

### B. Quickstart Commands

```bash
# 1. Install backend dependencies
cd backend
python -m pip install -r requirements.txt
cd ..

# 2. Generate the full synthetic dataset (5,000 employees, seed 20261022)
python scripts/generate_data.py --profile full --seed 20261022

# 3. Initialize and seed the SQLite database
python scripts/seed_database.py

# 4. Execute the 22-point structural validation check
python scripts/validate_data.py

# 5. Run the ground-truth evaluation pipeline
python scripts/calculate_metrics.py

# 6. Verify bitwise reproducibility
python scripts/check_reproducibility.py --profile starter

# 7. Run automated test suite
$env:PYTHONPATH="backend"  # On Windows PowerShell
pytest backend/tests -v

# 8. Start the FastAPI backend server
cd backend
uvicorn app.main:app --reload --port 8000
# Backend is live at http://127.0.0.1:8000 (Swagger docs at http://127.0.0.1:8000/docs)

# 9. In another terminal, start the React frontend
cd frontend
npm install
npm run dev
# Frontend is live at http://localhost:5173
```

---

## 6. Demo Accounts (Local Development)

| Username | Password | Role | Access Level |
| :--- | :--- | :--- | :--- |
| `admin` | `AdminPassword123!` | `system_admin` | Full administrative access, evaluations, approvals |
| `hr_lead` | `HrPassword123!` | `hr_partner` | Compensation reviews, proposal creation & submission |
| `dept_manager` | `ManagerPassword123!` | `manager` | Team overview & employee review access |
| `auditor` | `AuditorPassword123!` | `it_operations` | System health, evaluations, and audit viewer |
| `employee1` | `EmployeePassword123!` | `employee` | Self profile view |

*Note: The frontend includes a top-bar user switcher to effortlessly toggle between accounts.*

---

## 7. Automated Verification & Metrics Summary

- **Total Workforce Records:** exactly 5,000 employees
- **Distinct Role-Level Combinations:** exactly 200 combinations (25 roles $\times$ 8 levels)
- **Salary History:** 15,228 records covering 2024, 2025, and 2026
- **Structural Integrity Validation:** **22 / 22 CHECKS PASSED (100%)**
- **Evaluation against Isolated Ground Truth:**
  - **Precision:** 100.0%
  - **Recall:** 100.0%
  - **F1 Score:** 1.0000
- **Reproducibility:** 100% bitwise SHA-256 match across all CSV files.

---

## 8. Migration to PostgreSQL

To deploy against PostgreSQL in staging/production:
1. In `.env`, change `DATABASE_URL` to:
   ```env
   DATABASE_URL=postgresql+psycopg2://user:password@postgres-host:5432/compensation_equity
   ```
2. Run database migrations / seeding via `python scripts/seed_database.py`.
3. SQLAlchemy models use portable ANSI SQL types (`String`, `Integer`, `Float`, `Date`, `DateTime`, `Text`, `CheckConstraint`) with zero SQLite-specific vendor extensions.
