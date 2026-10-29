import React, { useEffect, useState } from 'react';
import { 
  ArrowLeft, Calendar, DollarSign, Award, Clock, 
  FileText, AlertTriangle, ShieldCheck, Plus, CheckCircle, Orbit 
} from 'lucide-react';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { BandTunnel3D } from '../components/BandTunnel3D';
import { AIAgentPanel } from '../components/AIAgentPanel';

interface EmployeeDetailProps {
  employeeId: string;
  onBack: () => void;
  currentUser: { username: string; role: string };
  onProposalCreated: () => void;
}

export const EmployeeDetailPage: React.FC<EmployeeDetailProps> = ({
  employeeId,
  onBack,
  currentUser,
  onProposalCreated,
}) => {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Proposal Modal State
  const [showModal, setShowModal] = useState(false);
  const [proposedSalary, setProposedSalary] = useState('');
  const [reasonCodes, setReasonCodes] = useState('MARKET_EQUITY');
  const [evidenceSummary, setEvidenceSummary] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [proposalMsg, setProposalMsg] = useState<string | null>(null);

  useEffect(() => {
    loadDetail();
  }, [employeeId]);

  const loadDetail = async () => {
    setLoading(true);
    try {
      const res = await api.getEmployeeAnalysis(employeeId);
      setData(res);
      if (res.analysis?.actual_base_salary) {
        setProposedSalary((res.analysis.actual_base_salary * 1.1).toFixed(0));
      }
    } catch (e: any) {
      setError(e.message || 'Failed to load employee details');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProposal = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setProposalMsg(null);
    try {
      await api.createProposal({
        employee_id: employeeId,
        proposed_salary: parseFloat(proposedSalary),
        proposed_currency: data.analysis.currency,
        reason_codes: reasonCodes,
        evidence_summary: evidenceSummary || 'Proposed based on compensation review and compa-ratio alignment.',
      });
      setProposalMsg('Proposal created successfully in Draft status.');
      setShowModal(false);
      loadDetail();
      onProposalCreated();
    } catch (err: any) {
      setProposalMsg(`Error: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-rose-50 p-6 rounded-xl border border-rose-200 text-center">
        <h3 className="font-semibold text-rose-800">Error loading employee</h3>
        <p className="text-xs text-rose-600 mt-1">{error}</p>
        <button onClick={onBack} className="mt-4 px-4 py-1.5 bg-rose-600 text-white rounded text-xs">
          Go Back
        </button>
      </div>
    );
  }

  const { employee, analysis, salary_history, performance_history, tenure_history, promotions, applicable_band } = data;

  return (
    <div className="space-y-6">
      {/* Back Button & Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
        <button
          onClick={onBack}
          className="flex items-center space-x-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Explorer</span>
        </button>
        <div className="flex items-center space-x-3">
          <StatusBadge status={analysis.status} />
          {currentUser.role !== 'employee' && (
            <button
              onClick={() => setShowModal(true)}
              className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold flex items-center space-x-1 shadow-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Propose Salary Adjustment</span>
            </button>
          )}
        </div>
      </div>

      {proposalMsg && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs p-3 rounded-lg flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 text-emerald-600" />
          <span>{proposalMsg}</span>
        </div>
      )}

      {/* Employee Profile Overview Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
        <div className="flex flex-col sm:flex-row justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3">
              <h2 className="text-2xl font-bold text-slate-900">{employee.first_name} {employee.last_name}</h2>
              <span className="font-mono text-xs text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
                {employee.employee_id}
              </span>
            </div>
            <div className="text-sm font-medium text-slate-600 mt-1">
              {employee.role_name} • <span className="text-indigo-600">{employee.level_name}</span>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div>
              <span className="text-slate-400 block uppercase font-medium">Location</span>
              <span className="font-semibold text-slate-800">{employee.location_name}</span>
            </div>
            <div>
              <span className="text-slate-400 block uppercase font-medium">Employment</span>
              <span className="font-semibold text-slate-800 capitalize">{employee.employment_type.replace('_', ' ')} (FTE {employee.fte})</span>
            </div>
            <div>
              <span className="text-slate-400 block uppercase font-medium">Hire Date</span>
              <span className="font-semibold text-slate-800 font-mono">{employee.hire_date}</span>
            </div>
            <div>
              <span className="text-slate-400 block uppercase font-medium">Tenure</span>
              <span className="font-semibold text-slate-800">{tenure_history[0]?.relevant_experience_months || 24} months</span>
            </div>
          </div>
        </div>
      </div>

      {/* Compensation Parity & Mathematical Breakdown */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
              <DollarSign className="w-5 h-5 text-indigo-600" />
              <span>Compensation Equity Analysis & Derived Math Breakdown</span>
            </h3>
            <p className="text-xs text-slate-500">
              Full transparency: see source values, currency exchange, FTE normalization, and band comparisons.
            </p>
          </div>
        </div>

        {/* 3D Spatial Band Tunnel */}
        {analysis.band_min && analysis.band_max && (
          <BandTunnel3D
            compaRatio={analysis.compa_ratio ?? 1.0}
            bandPosition={analysis.band_position ?? 50}
            minSalary={analysis.band_min}
            midSalary={analysis.band_mid || (analysis.band_min + analysis.band_max) / 2}
            maxSalary={analysis.band_max}
            actualSalary={analysis.normalized_fte_salary || analysis.actual_base_salary}
            currency={analysis.currency || 'USD'}
          />
        )}

        {/* AI Agent & Vector Intelligence Copilot */}
        <AIAgentPanel
          employeeId={employee.employee_code}
          compaRatio={analysis.compa_ratio ?? 1.0}
          bandPosition={analysis.band_position ?? 50.0}
          normalizedSalary={analysis.normalized_fte_salary || analysis.actual_base_salary}
          bandMid={analysis.band_mid}
          title={employee.title}
        />

        {/* Math Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          {/* Step 1: Base & Currency */}
          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2">
            <span className="font-bold text-slate-700 block uppercase tracking-wider text-[10px]">
              1. Base Paid Compensation
            </span>
            <div className="flex justify-between items-baseline">
              <span className="text-slate-500">Actual Base Salary:</span>
              <span className="font-mono font-bold text-slate-900 text-sm">
                {analysis.currency} {analysis.actual_base_salary.toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between items-baseline">
              <span className="text-slate-500">Effective Exchange Rate:</span>
              <span className="font-mono text-slate-800">
                1 {analysis.currency} = {analysis.exchange_rate} USD
              </span>
            </div>
            <div className="flex justify-between items-baseline border-t border-slate-200 pt-1.5">
              <span className="text-slate-500 font-medium">Annualized in USD:</span>
              <span className="font-mono font-semibold text-slate-900">
                ${(analysis.actual_base_salary * analysis.exchange_rate).toLocaleString()}
              </span>
            </div>
          </div>

          {/* Step 2: FTE Normalization */}
          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2">
            <span className="font-bold text-slate-700 block uppercase tracking-wider text-[10px]">
              2. Full-Time Equivalent (FTE)
            </span>
            <div className="flex justify-between items-baseline">
              <span className="text-slate-500">Recorded FTE:</span>
              <span className="font-mono font-bold text-slate-900">{analysis.fte}</span>
            </div>
            <div className="flex justify-between items-baseline">
              <span className="text-slate-500">Formula:</span>
              <span className="font-mono text-slate-600 text-[11px]">Annualized / FTE</span>
            </div>
            <div className="flex justify-between items-baseline border-t border-slate-200 pt-1.5">
              <span className="text-slate-700 font-medium">Normalized FTE Salary:</span>
              <span className="font-mono font-bold text-indigo-600 text-sm">
                ${analysis.normalized_fte_salary?.toLocaleString() || 'N/A'}
              </span>
            </div>
          </div>

          {/* Step 3: Applicable Band */}
          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2">
            <span className="font-bold text-slate-700 block uppercase tracking-wider text-[10px]">
              3. Applicable Compensation Band
            </span>
            <div className="flex justify-between items-baseline">
              <span className="text-slate-500">Band ID:</span>
              <span className="font-mono text-slate-800 text-[11px] truncate max-w-[160px]">
                {analysis.applicable_band_id || 'None'}
              </span>
            </div>
            <div className="flex justify-between items-baseline">
              <span className="text-slate-500">Band Range (USD):</span>
              <span className="font-mono text-slate-800">
                ${analysis.band_min?.toLocaleString()} – ${analysis.band_max?.toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between items-baseline border-t border-slate-200 pt-1.5">
              <span className="text-slate-500 font-medium">Midpoint Benchmark:</span>
              <span className="font-mono font-bold text-slate-900">
                ${analysis.band_mid?.toLocaleString() || 'N/A'}
              </span>
            </div>
          </div>
        </div>

        {/* Key Indicators Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
          {/* Compa-Ratio */}
          <div className="p-4 bg-indigo-50/50 rounded-lg border border-indigo-100 flex items-center justify-between">
            <div>
              <div className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Compa-Ratio</div>
              <div className="text-2xl font-bold text-indigo-700 font-mono mt-0.5">
                {analysis.compa_ratio ? analysis.compa_ratio.toFixed(4) : 'N/A'}
              </div>
              <p className="text-[11px] text-slate-500 mt-1 font-mono">Formula: Normalized Salary / Midpoint</p>
            </div>
            <div className="text-right">
              {analysis.compa_ratio && analysis.compa_ratio < 0.85 ? (
                <span className="text-xs bg-rose-100 text-rose-800 font-semibold px-2.5 py-1 rounded-full border border-rose-200">
                  Below Midpoint (&lt; 0.85)
                </span>
              ) : (
                <span className="text-xs bg-emerald-100 text-emerald-800 font-semibold px-2.5 py-1 rounded-full border border-emerald-200">
                  Healthy Alignment
                </span>
              )}
            </div>
          </div>

          {/* Within-Band Position */}
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between">
            <div className="w-2/3">
              <div className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Within-Band Position</div>
              <div className="text-2xl font-bold text-slate-900 font-mono mt-0.5">
                {analysis.band_position !== null ? `${analysis.band_position.toFixed(1)}%` : 'N/A'}
              </div>
              {/* Visual bar */}
              <div className="w-full bg-slate-200 h-2 rounded-full mt-2 overflow-hidden">
                <div 
                  className={`h-2 rounded-full ${
                    analysis.band_position < 0 ? 'bg-rose-500' : analysis.band_position > 100 ? 'bg-amber-500' : 'bg-emerald-500'
                  }`}
                  style={{ width: `${Math.max(0, Math.min(100, analysis.band_position || 50))}%` }}
                ></div>
              </div>
            </div>
            <div className="text-right">
              {analysis.is_below_band ? (
                <span className="text-xs bg-rose-100 text-rose-800 font-semibold px-2 py-1 rounded-full border border-rose-200">
                  Below Minimum (&lt; 0%)
                </span>
              ) : analysis.is_above_band ? (
                <span className="text-xs bg-amber-100 text-amber-800 font-semibold px-2 py-1 rounded-full border border-amber-200">
                  Above Maximum (&gt; 100%)
                </span>
              ) : (
                <span className="text-xs bg-emerald-100 text-emerald-800 font-semibold px-2 py-1 rounded-full border border-emerald-200">
                  In Band (0% – 100%)
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Flagged Reason Codes */}
        {analysis.exception_reasons && analysis.exception_reasons.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs space-y-1">
            <div className="font-semibold text-amber-800 flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <span>Flagged Reason Codes for Human Review:</span>
            </div>
            <ul className="list-disc list-inside text-amber-700 pl-2">
              {analysis.exception_reasons.map((r: string, idx: number) => (
                <li key={idx}>{r}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Salary History Timeline */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
        <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center space-x-2">
          <Calendar className="w-4 h-4 text-indigo-600" />
          <span>3-Year Historical Salary Records (2024 – 2026)</span>
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 text-slate-500 font-semibold uppercase border-b border-slate-200">
                <th className="py-2.5 px-3">Effective Date</th>
                <th className="py-2.5 px-3">Salary ID</th>
                <th className="py-2.5 px-3">Base Amount</th>
                <th className="py-2.5 px-3">Currency</th>
                <th className="py-2.5 px-3">FTE</th>
                <th className="py-2.5 px-3">Salary Type</th>
                <th className="py-2.5 px-3">Source Event</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {salary_history.map((s: any) => (
                <tr key={s.salary_record_id} className="hover:bg-slate-50">
                  <td className="py-2.5 px-3 font-mono font-medium">{s.effective_date}</td>
                  <td className="py-2.5 px-3 font-mono text-indigo-600">{s.salary_id}</td>
                  <td className="py-2.5 px-3 font-mono font-bold text-slate-900">{s.base_salary.toLocaleString()}</td>
                  <td className="py-2.5 px-3">{s.currency_code}</td>
                  <td className="py-2.5 px-3 font-mono">{s.fte_at_record}</td>
                  <td className="py-2.5 px-3 capitalize">{s.salary_type.replace('_', ' ')}</td>
                  <td className="py-2.5 px-3 text-slate-400 font-mono text-[11px]">{s.source_event_id || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Performance Reviews Evidence */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
        <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center space-x-2">
          <Award className="w-4 h-4 text-indigo-600" />
          <span>Performance Evidence & Documented Ratings</span>
        </h3>
        <div className="space-y-3 text-xs">
          {performance_history.length === 0 ? (
            <p className="text-slate-400">No performance records documented.</p>
          ) : (
            performance_history.map((p: any) => (
              <div key={p.evidence_id} className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-start justify-between">
                <div>
                  <div className="font-semibold text-slate-800">
                    Review Period: {p.review_period_start} to {p.review_period_end}
                  </div>
                  <p className="text-slate-600 mt-1">{p.documented_summary}</p>
                  <span className="text-[10px] text-slate-400 font-mono mt-1 block">Ref: {p.source_reference}</span>
                </div>
                <div className="text-right ml-4">
                  <div className="text-lg font-bold text-indigo-600 font-mono">
                    {p.performance_rating} / {p.rating_scale_max}
                  </div>
                  <span className="text-[10px] text-slate-400 uppercase font-medium">{p.evidence_category.replace('_', ' ')}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Proposal Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Propose Compensation Adjustment</h3>
            <p className="text-xs text-slate-500">
              Submit an evidence-based pay equity review proposal for {employee.first_name} {employee.last_name}.
            </p>

            <form onSubmit={handleCreateProposal} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Proposed Annual Salary ({analysis.currency})</label>
                <input
                  type="number"
                  step="100"
                  required
                  value={proposedSalary}
                  onChange={(e) => setProposedSalary(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg p-2 text-sm font-mono focus:ring-2 focus:ring-indigo-500"
                />
                <span className="text-[11px] text-slate-400 mt-0.5 block">
                  Current: {analysis.currency} {analysis.actual_base_salary.toLocaleString()}
                </span>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Reason Codes</label>
                <select
                  value={reasonCodes}
                  onChange={(e) => setReasonCodes(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg p-2"
                >
                  <option value="MARKET_EQUITY">Market Equity Adjustment</option>
                  <option value="PROMOTION_ALIGNMENT">Promotion Pay Realignment</option>
                  <option value="BAND_MINIMUM_CORRECTION">Correction to Band Minimum</option>
                  <option value="EXEMPLARY_PERFORMANCE">Merit / Exemplary Performance</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Evidence Summary & Documented Justification</label>
                <textarea
                  rows={3}
                  required
                  placeholder="Document the peer comparison, performance rating history, and justification..."
                  value={evidenceSummary}
                  onChange={(e) => setEvidenceSummary(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg p-2"
                />
              </div>

              <div className="pt-3 border-t border-slate-200 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 font-medium hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 disabled:opacity-50"
                >
                  {submitting ? 'Submitting...' : 'Create Draft Proposal'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
