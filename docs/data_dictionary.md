# Data Dictionary & Entity Specifications

## 1. Role (`roles`)
| Field | Type | Required | Uniqueness | Allowed Values / Constraints | Relationships | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `role_id` | String(50) | Yes | Primary Key | Format `ROL-<CODE>` | Parent of Employee, Band | Master job role identifier |
| `role_code` | String(50) | Yes | Unique | e.g. `SWE`, `PM`, `DE` | None | Business role abbreviation |
| `role_name` | String(100) | Yes | No | e.g. "Software Engineer" | None | Descriptive title |
| `job_family` | String(50) | Yes | No | Engineering, Product, Design, Sales, etc. | None | Functional family |
| `job_function` | String(50) | Yes | No | Technical specialization | None | Sub-domain function |
| `description` | Text | No | No | Free text | None | Job description summary |
| `active_status`| Boolean | Yes | No | True, False | None | Operational status |

---

## 2. Level (`levels`)
| Field | Type | Required | Uniqueness | Allowed Values / Constraints | Relationships | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `level_id` | String(50) | Yes | Primary Key | Format `LEV-<CODE>` | Parent of Employee, Band | Master career level identifier |
| `level_code` | String(50) | Yes | Unique | e.g. `IC1`, `IC2`, `M1` | None | Level code |
| `level_name` | String(100) | Yes | No | e.g. "Senior Software Engineer"| None | Descriptive level title |
| `level_rank` | Integer | Yes | No | 1, 2, 3, 4, 5 | None | Numerical rank for hierarchy |
| `career_track`| String(50) | Yes | No | `individual_contributor`, `management`, `specialist` | None | Career ladder track |
| `active_status`| Boolean | Yes | No | True, False | None | Operational status |

---

## 3. Location (`locations`)
| Field | Type | Required | Uniqueness | Allowed Values / Constraints | Relationships | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `location_id` | String(50) | Yes | Primary Key | Format `LOC-<CTRY>-<CITY>` | Parent of Employee, Band | Master location identifier |
| `location_code`| String(50) | Yes | Unique | e.g. `IN-BLR`, `US-NYC` | None | Business location code |
| `city` | String(100) | Yes | No | e.g. Bangalore, New York | None | Office city |
| `region` | String(100) | Yes | No | State or province | None | Geographic region |
| `country` | String(100) | Yes | No | India, United States, UK, Germany, Singapore | None | Country name |
| `currency_code`| String(10) | Yes | No | INR, USD, GBP, EUR, SGD | References ExchangeRate | Local operational currency |
| `cost_of_labor_zone`| String(50) | Yes | No | Zone 1, Zone 2, Zone 3 | None | Market geographic pay zone |
| `active_status`| Boolean | Yes | No | True, False | None | Operational status |

---

## 4. CompensationBand (`compensation_bands`)
| Field | Type | Required | Uniqueness | Allowed Values / Constraints | Relationships | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `band_id` | String(100) | Yes | Primary Key | `BAND-<role>-<level>-<location>-<year>` | None | Deterministic band identifier |
| `role_id` | String(50) | Yes | No | Foreign Key | Roles | Linked role |
| `level_id` | String(50) | Yes | No | Foreign Key | Levels | Linked career level |
| `location_id` | String(50) | Yes | No | Foreign Key | Locations | Linked location |
| `effective_start_date` | Date | Yes | No | ISO Date | None | Band validity start date |
| `effective_end_date` | Date | No | No | Nullable or >= start_date | None | Band validity end date |
| `minimum_salary` | Float | Yes | No | Positive float | None | Lower band boundary |
| `midpoint_salary`| Float | Yes | No | min < mid < max | None | Midpoint market benchmark |
| `maximum_salary` | Float | Yes | No | max > mid | None | Upper band boundary |
| `currency_code` | String(10) | Yes | No | INR, USD, GBP, EUR, SGD | ExchangeRate | Band currency |
| `annual_basis` | Boolean | Yes | No | True | None | Stored on annual basis |
| `band_version` | Integer | Yes | No | Positive integer | None | Revisions counter |
| `created_at` | DateTime | Yes | No | ISO Timestamp | None | Audit timestamp |

---

## 5. Employee (`employees`)
| Field | Type | Required | Uniqueness | Allowed Values / Constraints | Relationships | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `employee_id` | String(50) | Yes | Primary Key | `EMP-000001` (zero-padded) | Parent of Salaries, Reviews | Synthetic employee identifier |
| `employee_code` | String(50) | Yes | Unique | `EC-000001` | None | Business employee code |
| `first_name` | String(100) | Yes | No | Fictional name | None | Synthetic first name |
| `last_name` | String(100) | Yes | No | Fictional name | None | Synthetic surname |
| `role_id` | String(50) | Yes | No | Foreign Key | Roles | Active role |
| `level_id` | String(50) | Yes | No | Foreign Key | Levels | Active level |
| `location_id` | String(50) | Yes | No | Foreign Key | Locations | Primary work location |
| `employment_type`| String(50) | Yes | No | `full_time`, `part_time`, `contract` | None | Employment relationship |
| `fte` | Float | Yes | No | `0.10 <= fte <= 1.00` | None | Full-time equivalent fraction |
| `hire_date` | Date | Yes | No | ISO Date | None | Company join date |
| `termination_date`| Date | No | No | Nullable or >= hire_date | None | Separation date |
| `employment_status`| String(50)| Yes | No | `active`, `on_leave`, `terminated` | None | Current workforce status |
| `manager_employee_id`| String(50)| No | No | Self-referencing FK | Employee | Direct manager |
| `created_at` | DateTime | Yes | No | ISO Timestamp | None | Record creation timestamp |
| `updated_at` | DateTime | Yes | No | ISO Timestamp | None | Record update timestamp |

---

## 6. SalaryRecord (`salary_records`)
| Field | Type | Required | Uniqueness | Constraints | Relationships | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `salary_record_id` | String(50) | Yes | Primary Key | `SR-000001` | Parent of Proposals | Transactional salary row |
| `employee_id` | String(50) | Yes | No | Foreign Key | Employee | Subject employee |
| `salary_id` | String(100) | Yes | No | `SAL-<EMP>-<YYYY>-<MM>` | None | Deterministic monthly salary key |
| `effective_date` | Date | Yes | No | ISO Date | None | Effective date of compensation |
| `base_salary` | Float | Yes | No | `base_salary > 0` | None | Paid base gross salary |
| `currency_code` | String(10) | Yes | No | Valid currency code | ExchangeRate | Currency of payment |
| `fte_at_record` | Float | Yes | No | `0.10 <= fte <= 1.00` | None | FTE fraction at record date |
| `annualized_salary` | Float | Yes | No | Derived (monthly * 12 or annual) | None | Annualized base compensation |
| `salary_type` | String(50) | Yes | No | base_salary, merit_increase, promotion, market_adjustment | None | Transaction reason |
| `source_event_id` | String(50) | No | No | Cycle ID or Proposal ID | AdjustmentProposal | Provenance correlation |

---

## 7. AdjustmentProposal (`adjustment_proposals`)
| Field | Type | Required | State Constraints | Relationships | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `adjustment_id` | String(50) | Yes | Primary Key (`ADJ-2026-000001`) | Parent of Events | Proposal identifier |
| `employee_id` | String(50) | Yes | Foreign Key | Employee | Target employee |
| `salary_record_id` | String(50) | Yes | Foreign Key | SalaryRecord | Base salary record reference |
| `applicable_band_id`| String(100)| No | Nullable FK | CompensationBand | Benchmark band evaluated |
| `proposed_salary` | Float | Yes | Positive float | None | Proposed new base salary |
| `proposed_currency`| String(10)| Yes | Matches local currency | None | Currency of proposal |
| `normalized_current_salary`| Float | Yes | Derived in USD | None | Baseline normalized comp |
| `normalized_proposed_salary`| Float | Yes | Derived in USD | None | Target normalized comp |
| `reason_codes` | String | Yes | Documented codes | None | Comma-separated reason codes |
| `evidence_summary` | Text | Yes | Non-empty | None | Documented HR justification |
| `proposal_status` | String(50) | Yes | `draft -> pending_review -> approved / rejected / returned_for_revision -> applied` | None | Lifecycle state |
| `created_by` | String(100) | Yes | User username | User | Initiator |
| `approved_by` | String(100) | No | Must not equal created_by | User | Designated dual approver |
| `version_number` | Integer | Yes | Increments on state transition | None | Optimistic locking counter |
