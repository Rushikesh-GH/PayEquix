import React, { useEffect, useState } from 'react';
import { 
  FileText, CheckCircle, XCircle, RotateCcw, 
  Send, Play, AlertCircle, ArrowRight, ShieldCheck 
} from 'lucide-react';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { ProposalFlowCylinder3D } from '../components/ProposalFlowCylinder3D';
import { Card3D } from '../components/Card3D';
import { AdjustmentProposal } from '../types';

interface ProposalsPageProps {
  onSelectEmployee: (empId: string) => void;
  currentUser: { username: string; role: string };
}

export const ProposalsPage: React.FC<ProposalsPageProps> = ({ onSelectEmployee, currentUser }) => {
  const [proposals, setProposals] = useState<AdjustmentProposal[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState('');

  // Action modal state
  const [activeProposal, setActiveProposal] = useState<AdjustmentProposal | null>(null);
  const [actionType, setActionType] = useState<'submit' | 'approve' | 'reject' | 'return' | 'apply' | null>(null);
  const [comments, setComments] = useState('');
  const [processing, setProcessing] = useState(false);
  const [alertMsg, setAlertMsg] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    loadProposals();
  }, [selectedStatus]);

  const loadProposals = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams(selectedStatus ? { status: selectedStatus } : {});
      const data = await api.getProposals(params.toString());
      setProposals(data);
    } catch (e) {
      console.error('Failed to load proposals', e);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteAction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeProposal || !actionType) return;
    setProcessing(true);
    setAlertMsg(null);
    try {
      if (actionType === 'submit') {
        await api.submitProposal(activeProposal.adjustment_id, comments || 'Submitted for approval');
      } else if (actionType === 'approve') {
        await api.approveProposal(activeProposal.adjustment_id, comments || 'Approved by authorized reviewer');
      } else if (actionType === 'reject') {
        await api.rejectProposal(activeProposal.adjustment_id, comments || 'Rejected proposal');
      } else if (actionType === 'return') {
        await api.returnProposal(activeProposal.adjustment_id, comments || 'Returned for revision');
      } else if (actionType === 'apply') {
        await api.applyProposal(activeProposal.adjustment_id, comments || 'Applied approved salary adjustment');
      }

      setAlertMsg({
        text: `Proposal ${activeProposal.adjustment_id} successfully executed: ${actionType.toUpperCase()}`,
        type: 'success',
      });
      setActiveProposal(null);
      setActionType(null);
      setComments('');
      loadProposals();
    } catch (err: any) {
      setAlertMsg({ text: `Failed to execute action: ${err.message}`, type: 'error' });
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-slate-700/60">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white drop-shadow-sm">Adjustment Review Queue</h1>
          <p className="text-sm text-slate-300 mt-1">
            Human-in-the-loop review proposals: separation of duties, approval workflows, and immutable audit trails.
          </p>
        </div>
        <div className="text-xs bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 px-3.5 py-1.5 rounded-xl flex items-center space-x-2">
          <ShieldCheck className="w-4 h-4 text-indigo-400" />
          <span>Role-Based Separation of Duties Active</span>
        </div>
      </div>

      {alertMsg && (
        <div
          className={`border text-xs p-3.5 rounded-lg flex items-center space-x-2 ${
            alertMsg.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          }`}
        >
          {alertMsg.type === 'success' ? (
            <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          )}
          <span>{alertMsg.text}</span>
        </div>
      )}

      {/* 3D Workflow Pipeline Lifecycle */}
      <ProposalFlowCylinder3D
        statusCounts={proposals.reduce((acc: Record<string, number>, p) => {
          const st = p.proposal_status.toLowerCase();
          acc[st] = (acc[st] || 0) + 1;
          return acc;
        }, {})}
      />

      {/* Filter Tabs */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs">
        {['', 'pending_review', 'approved', 'applied', 'draft', 'rejected', 'returned_for_revision'].map((st) => (
          <button
            key={st}
            onClick={() => setSelectedStatus(st)}
            className={`px-3 py-1.5 rounded-lg font-medium capitalize transition-colors ${
              selectedStatus === st
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {st ? st.replace(/_/g, ' ') : 'All Proposals'}
          </button>
        ))}
      </div>

      {/* Proposals Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Proposal ID</th>
                <th className="py-3 px-4">Employee</th>
                <th className="py-3 px-4">Current Salary</th>
                <th className="py-3 px-4">Proposed Salary</th>
                <th className="py-3 px-4">Delta</th>
                <th className="py-3 px-4">Reason Codes</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-2"></div>
                    Loading proposals...
                  </td>
                </tr>
              ) : proposals.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500">
                    No proposals found matching filter.
                  </td>
                </tr>
              ) : (
                proposals.map((p) => {
                  const diff = p.proposed_salary - p.normalized_current_salary;
                  const pct = ((diff / p.normalized_current_salary) * 100).toFixed(1);
                  const isCreator = p.created_by === currentUser.username;
                  const canApprove =
                    p.proposal_status === 'pending_review' &&
                    (currentUser.role === 'system_admin' || (currentUser.role === 'hr_partner' && !isCreator));

                  return (
                    <tr key={p.adjustment_id} className="hover:bg-slate-50">
                      <td className="py-3.5 px-4 font-mono font-medium text-indigo-600">
                        {p.adjustment_id}
                        <div className="text-[10px] text-slate-400">v{p.version_number} by {p.created_by}</div>
                      </td>
                      <td className="py-3.5 px-4 font-mono">
                        <button
                          onClick={() => onSelectEmployee(p.employee_id)}
                          className="text-slate-900 font-semibold hover:text-indigo-600 flex items-center space-x-1"
                        >
                          <span>{p.employee_id}</span>
                          <ArrowRight className="w-3 h-3 text-slate-400" />
                        </button>
                      </td>
                      <td className="py-3.5 px-4 font-mono">
                        {p.proposed_currency} {p.normalized_current_salary.toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 font-mono font-bold text-slate-900">
                        {p.proposed_currency} {p.proposed_salary.toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 font-mono font-semibold text-emerald-600">
                        +{pct}%
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="text-[11px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-mono">
                          {p.reason_codes}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <StatusBadge status={p.proposal_status} />
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end space-x-1.5">
                          {p.proposal_status === 'draft' && (
                            <button
                              onClick={() => { setActiveProposal(p); setActionType('submit'); }}
                              className="px-2.5 py-1 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded font-medium flex items-center space-x-1"
                            >
                              <Send className="w-3 h-3" />
                              <span>Submit</span>
                            </button>
                          )}

                          {p.proposal_status === 'pending_review' && (
                            <>
                              <button
                                disabled={!canApprove}
                                title={isCreator ? 'Creator cannot approve their own proposal' : 'Approve proposal'}
                                onClick={() => { setActiveProposal(p); setActionType('approve'); }}
                                className="px-2.5 py-1 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 disabled:opacity-40 rounded font-medium flex items-center space-x-1"
                              >
                                <CheckCircle className="w-3 h-3" />
                                <span>Approve</span>
                              </button>
                              <button
                                onClick={() => { setActiveProposal(p); setActionType('reject'); }}
                                className="px-2.5 py-1 bg-rose-50 text-rose-700 hover:bg-rose-100 rounded font-medium flex items-center space-x-1"
                              >
                                <XCircle className="w-3 h-3" />
                                <span>Reject</span>
                              </button>
                            </>
                          )}

                          {p.proposal_status === 'approved' && (
                            <button
                              onClick={() => { setActiveProposal(p); setActionType('apply'); }}
                              className="px-2.5 py-1 bg-emerald-600 text-white hover:bg-emerald-700 rounded font-semibold flex items-center space-x-1 shadow-xs"
                            >
                              <Play className="w-3 h-3" />
                              <span>Apply Adjustment</span>
                            </button>
                          )}

                          {p.proposal_status === 'applied' && (
                            <span className="text-[11px] font-mono text-slate-400">Reconciled</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Action Confirmation Modal */}
      {activeProposal && actionType && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <h3 className="text-lg font-bold text-slate-900 capitalize">
              Confirm Workflow Action: {actionType}
            </h3>

            <div className="text-xs bg-slate-50 p-3 rounded-lg border border-slate-200 space-y-1 font-mono">
              <div>Proposal: <span className="font-bold text-slate-800">{activeProposal.adjustment_id}</span></div>
              <div>Employee: {activeProposal.employee_id}</div>
              <div>Proposed: {activeProposal.proposed_currency} {activeProposal.proposed_salary.toLocaleString()}</div>
            </div>

            {actionType === 'apply' && (
              <div className="bg-amber-50 border border-amber-200 text-amber-800 text-xs p-3 rounded-lg">
                <strong>Attention:</strong> Applying this proposal will write a new SalaryRecord effective immediately and update employee historical compa-ratio. This action is irreversible.
              </div>
            )}

            <form onSubmit={handleExecuteAction} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Audit Comments / Justification</label>
                <textarea
                  rows={2}
                  required
                  placeholder="Record your workflow review comments for the audit log..."
                  value={comments}
                  onChange={(e) => setComments(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg p-2"
                />
              </div>

              <div className="pt-2 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => { setActiveProposal(null); setActionType(null); }}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 font-medium hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={processing}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 disabled:opacity-50"
                >
                  {processing ? 'Processing...' : `Confirm ${actionType.toUpperCase()}`}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
