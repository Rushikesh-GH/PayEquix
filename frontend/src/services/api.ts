const API_BASE = '/api/v1';

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('token');
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
    // AI Agents & Vector DB
  searchPoliciesVector: (query: string, topK: number = 3) =>
    fetchApi<any>(`/ai/vector-search?query=${encodeURIComponent(query)}&top_k=${topK}`),
  getCrewTriage: (employeeId: string, params: string = '') =>
    fetchApi<any>(`/ai/crew-triage/${employeeId}?${params}`),
};

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Auth
  login: (username: string, password: string) =>
    fetchApi<any>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  // System
  getSystemInfo: () => fetchApi<any>('/system/info'),
  getExecutiveMetrics: () => fetchApi<any>('/system/metrics'),

  // Master Data
  getRoles: () => fetchApi<any[]>('/roles'),
  getLevels: () => fetchApi<any[]>('/levels'),
  getLocations: () => fetchApi<any[]>('/locations'),
  getBands: (params: string = '') => fetchApi<any[]>(`/bands?${params}`),

  // Employees
  getEmployees: (params: string = '') => fetchApi<any>(`/employees?${params}`),
  getEmployeeDetail: (employeeId: string) => fetchApi<any>(`/employees/${employeeId}`),
  getEmployeeAnalysis: (employeeId: string) => fetchApi<any>(`/employees/${employeeId}/compensation-analysis`),

  // Compensation
  getAllAnalysis: (params: string = '') => fetchApi<any>(`/compensation/analysis?${params}`),

  // Exceptions
  getExceptions: (params: string = '') => fetchApi<any[]>(`/exceptions?${params}`),
  updateExceptionStatus: (issueId: string, status: string, rationale: string) =>
    fetchApi<any>(`/exceptions/${issueId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status, rationale }),
    }),

  // Proposals
  getProposals: (params: string = '') => fetchApi<any[]>(`/proposals?${params}`),
  getProposalDetail: (id: string) => fetchApi<any>(`/proposals/${id}`),
  createProposal: (payload: any) =>
    fetchApi<any>('/proposals', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  submitProposal: (id: string, comments: string) =>
    fetchApi<any>(`/proposals/${id}/submit`, {
      method: 'POST',
      body: JSON.stringify({ comments }),
    }),
  approveProposal: (id: string, comments: string) =>
    fetchApi<any>(`/proposals/${id}/approve`, {
      method: 'POST',
      body: JSON.stringify({ comments }),
    }),
  rejectProposal: (id: string, comments: string) =>
    fetchApi<any>(`/proposals/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify({ comments }),
    }),
  returnProposal: (id: string, comments: string) =>
    fetchApi<any>(`/proposals/${id}/return`, {
      method: 'POST',
      body: JSON.stringify({ comments }),
    }),
  applyProposal: (id: string, comments: string) =>
    fetchApi<any>(`/proposals/${id}/apply`, {
      method: 'POST',
      body: JSON.stringify({ comments }),
    }),

  // Groups
  getComparableGroups: () => fetchApi<any[]>('/comparable-groups'),
  getComparableGroupDetail: (id: string) => fetchApi<any>(`/comparable-groups/${id}`),

  // Audit
  getAuditEvents: (params: string = '') => fetchApi<any[]>(`/audit/events?${params}`),

  // Data & Evaluation
  getDataQualitySummary: () => fetchApi<any>('/data-quality/summary'),
  getEvaluationSummary: () => fetchApi<any>('/evaluation/summary'),
  // AI Agents & Vector DB
  searchPoliciesVector: (query: string, topK: number = 3) =>
    fetchApi<any>(`/ai/vector-search?query=${encodeURIComponent(query)}&top_k=${topK}`),
  getCrewTriage: (employeeId: string, params: string = '') =>
    fetchApi<any>(`/ai/crew-triage/${employeeId}?${params}`),
};
