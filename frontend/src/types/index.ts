export interface Role {
  role_id: string;
  role_code: string;
  role_name: string;
  job_family: string;
  job_function: string;
  description?: string;
  active_status: boolean;
}

export interface Level {
  level_id: string;
  level_code: string;
  level_name: string;
  level_rank: number;
  career_track: string;
  active_status: boolean;
}

export interface Location {
  location_id: string;
  location_code: string;
  city: string;
  region: string;
  country: string;
  currency_code: string;
  cost_of_labor_zone: string;
  active_status: boolean;
}

export interface CompensationBand {
  band_id: string;
  role_id: string;
  level_id: string;
  location_id: string;
  effective_start_date: string;
  effective_end_date?: string;
  minimum_salary: number;
  midpoint_salary: number;
  maximum_salary: number;
  currency_code: string;
  annual_basis: boolean;
  band_version: number;
}

export interface EmployeeListItem {
  employee_id: string;
  employee_code: string;
  first_name: string;
  last_name: string;
  role_id: string;
  role_name: string;
  level_id: string;
  level_name: string;
  location_id: string;
  location_name: string;
  employment_type: string;
  fte: number;
  hire_date: string;
  employment_status: string;
  manager_employee_id?: string;
}

export interface CompensationAnalysisResult {
  employee_id: string;
  employee_name: string;
  role_id: string;
  role_name: string;
  level_id: string;
  level_name: string;
  location_id: string;
  location_name: string;
  currency: string;
  actual_base_salary: number;
  fte: number;
  annualized_salary: number;
  reporting_currency: string;
  exchange_rate: number;
  normalized_fte_salary: number;
  applicable_band_id?: string;
  band_min?: number;
  band_mid?: number;
  band_max?: number;
  compa_ratio?: number;
  band_position?: number;
  is_below_band: boolean;
  is_above_band: boolean;
  is_underpaid_midpoint: boolean;
  comparable_group_id?: string;
  comparable_group_size?: number;
  group_median_salary?: number;
  is_group_outlier: boolean;
  status: 'VALID' | 'REVIEW_CANDIDATE' | 'DATA_QUALITY_EXCEPTION';
  exception_reasons: string[];
  has_active_proposal: boolean;
}

export interface ExecutiveMetrics {
  total_employees: number;
  valid_comparisons_count: number;
  review_candidates_count: number;
  data_quality_exceptions_count: number;
  below_band_count: number;
  above_band_count: number;
  pending_proposals_count: number;
  approved_proposals_count: number;
  applied_proposals_count: number;
  avg_compa_ratio?: number;
  comparable_groups_count: number;
  data_validation_status: string;
  exception_type_counts: Record<string, number>;
  proposal_status_counts: Record<string, number>;
  compa_ratio_distribution: { bucket: string; count: number }[];
  band_position_distribution: { bucket: string; count: number }[];
  historical_trends: { year: string; avg_salary_usd: number; review_candidates: number; avg_compa_ratio: number }[];
}

export interface DataQualityIssue {
  issue_id: string;
  issue_type: string;
  entity_type: string;
  entity_id: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  description: string;
  expected_behavior: string;
  observed_behavior: string;
  detection_rule: string;
  status: 'DETECTED' | 'INVESTIGATED' | 'RESOLVED' | 'DISMISSED';
  documented_rationale?: string;
  created_at: string;
  resolved_at?: string;
}

export interface AdjustmentProposal {
  adjustment_id: string;
  employee_id: string;
  salary_record_id: string;
  applicable_band_id?: string;
  proposed_salary: number;
  proposed_currency: string;
  normalized_current_salary: number;
  normalized_proposed_salary: number;
  reason_codes: string;
  evidence_summary: string;
  estimated_band_position_before: number;
  estimated_band_position_after: number;
  proposal_status: 'draft' | 'pending_review' | 'approved' | 'rejected' | 'returned_for_revision' | 'applied';
  created_by: string;
  created_at: string;
  reviewed_by?: string;
  reviewed_at?: string;
  approved_by?: string;
  approved_at?: string;
  effective_date?: string;
  version_number: number;
}

export interface ComparableGroup {
  group_id: string;
  group_code: string;
  group_name: string;
  role_id: string;
  level_id: string;
  location_zone: string;
  min_size: number;
  is_active: boolean;
  equivalency_rationale?: string;
  approved_by?: string;
  is_equivalent_group: boolean;
  created_at: string;
  member_count: number;
  median_normalized_salary?: number;
  q1_salary?: number;
  q3_salary?: number;
}

export interface AuditEvent {
  event_id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  actor: string;
  timestamp: string;
  before_values?: string;
  after_values?: string;
  reason: string;
  correlation_id: string;
}
