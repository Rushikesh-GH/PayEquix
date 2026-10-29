import React, { useEffect, useState } from 'react';
import { 
  AlertTriangle, Filter, CheckCircle2, 
  HelpCircle, ShieldAlert, ArrowRight, MessageSquare 
} from 'lucide-react';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { ExceptionTriageRadar3D } from '../components/ExceptionTriageRadar3D';
import { Card3D } from '../components/Card3D';
import { DataQualityIssue } from '../types';

interface ExceptionsPageProps {
  onSelectEmployee: (empId: string) => void;
  currentUser: { username: string; role: string };
}

export const ExceptionsPage: React.FC<ExceptionsPageProps> = ({ onSelectEmployee, currentUser }) => {
  const [issues, setIssues] = useState<DataQualityIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSeverity, setSelectedSeverity] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');

  // Resolution modal state
  const [activeIssue, setActiveIssue] = useState<DataQualityIssue | null>(null);
  const [newStatus, setNewStatus] = useState<'INVESTIGATED' | 'RESOLVED' | 'DISMISSED'>('INVESTIGATED');
  const [rationale, setRationale] = useState('');
  const [updating, setUpdating] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadIssues();
  }, [selectedSeverity, selectedStatus]);

  const loadIssues = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        ...(selectedSeverity ? { severity: selectedSeverity } : {}),
        ...(selectedStatus ? { status: selectedStatus } : {}),
      });
      const data = await api.getExceptions(params.toString());
      setIssues(data);
    } catch (e) {
      console.error('Failed to load exceptions', e);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeIssue) return;
    setUpdating(true);
    setActionSuccess(null);
    try {
      await api.updateExceptionStatus(activeIssue.issue_id, newStatus, rationale);
      setActionSuccess(`Issue ${activeIssue.issue_id} updated to ${newStatus}. Audit event recorded.`);
      setActiveIssue(null);
      setRationale('');
      loadIssues();
    } catch (err: any) {
      alert(`Error updating exception: ${err.message}`);
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-slate-700/60">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white drop-shadow-sm">Exceptions Workbench</h1>
          <p className="text-sm text-slate-300 mt-1">
            Identify data-quality failures (expired bands, currency defects, FTE errors) and isolate them from parity reviews.
          </p>
        </div>
        <div className="text-xs bg-amber-500/15 text-amber-300 border border-amber-500/30 px-3.5 py-1.5 rounded-xl flex items-center space-x-2">
          <ShieldAlert className="w-4 h-4 text-amber-400" />
          <span>Investigation Signal Guardrail Active</span>
        </div>
      </div>

      {actionSuccess && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs p-3 rounded-lg flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* 3D Exception Triage Radar & Spatial Defect Map */}
      <ExceptionTriageRadar3D
        exceptionCounts={issues.reduce((acc: Record<string, number>, curr) => {
          acc[curr.issue_type] = (acc[curr.issue_type] || 0) + 1;
          return acc;
        }, {})}
      />

      {/* Filter Toolbar */}
      <Card3D glowColor="rose" className="p-4 flex flex-wrap gap-4 text-xs">
        <div>
          <label className="block text-slate-700 mb-1 font-semibold">Severity</label>
          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="border border-slate-300 rounded-lg p-2 min-w-[150px] bg-white text-slate-900 font-medium shadow-xs focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
          >
            <option value="" className="text-slate-900 bg-white">All Severities</option>
            <option value="CRITICAL" className="text-slate-900 bg-white">Critical</option>
            <option value="HIGH" className="text-slate-900 bg-white">High</option>
            <option value="MEDIUM" className="text-slate-900 bg-white">Medium</option>
            <option value="LOW" className="text-slate-900 bg-white">Low</option>
          </select>
        </div>

        <div>
          <label className="block text-slate-700 mb-1 font-semibold">Lifecycle Status</label>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="border border-slate-300 rounded-lg p-2 min-w-[150px] bg-white text-slate-900 font-medium shadow-xs focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
          >
            <option value="" className="text-slate-900 bg-white">All Statuses</option>
            <option value="DETECTED" className="text-slate-900 bg-white">Detected</option>
            <option value="INVESTIGATED" className="text-slate-900 bg-white">Investigated</option>
            <option value="RESOLVED" className="text-slate-900 bg-white">Resolved</option>
            <option value="DISMISSED" className="text-slate-900 bg-white">Dismissed</option>
          </select>
        </div>
      </Card3D>

      {/* Issues Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Issue ID & Type</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Entity Ref</th>
                <th className="py-3 px-4">Observed vs Expected</th>
                <th className="py-3 px-4">Rule Identifier</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-2"></div>
                    Loading exceptions...
                  </td>
                </tr>
              ) : issues.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    No exceptions found matching filter criteria.
                  </td>
                </tr>
              ) : (
                issues.map((iss) => (
                  <tr key={iss.issue_id} className="hover:bg-slate-50">
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-900">{iss.issue_type.replace(/_/g, ' ')}</div>
                      <div className="font-mono text-indigo-600 text-[11px]">{iss.issue_id}</div>
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={iss.severity} />
                    </td>
                    <td className="py-3 px-4 font-mono font-medium">
                      {iss.entity_id.startsWith('EMP-') ? (
                        <button
                          onClick={() => onSelectEmployee(iss.entity_id)}
                          className="text-indigo-600 hover:underline flex items-center space-x-1"
                        >
                          <span>{iss.entity_id}</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                      ) : (
                        <span>{iss.entity_id}</span>
                      )}
                    </td>
                    <td className="py-3 px-4 max-w-sm">
                      <div className="text-slate-900 font-medium">{iss.description}</div>
                      <div className="text-[11px] text-slate-500 mt-0.5">
                        <span className="font-semibold text-slate-600">Observed:</span> {iss.observed_behavior}
                      </div>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-500">{iss.detection_rule}</td>
                    <td className="py-3 px-4">
                      <StatusBadge status={iss.status} />
                    </td>
                    <td className="py-3 px-4 text-right">
                      {currentUser.role !== 'employee' && (
                        <button
                          onClick={() => {
                            setActiveIssue(iss);
                            setNewStatus(iss.status === 'DETECTED' ? 'INVESTIGATED' : 'RESOLVED');
                            setRationale(iss.documented_rationale || '');
                          }}
                          className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded text-[11px] transition-colors"
                        >
                          Action
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Resolution Modal */}
      {activeIssue && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Update Exception Investigation Status</h3>
            <div className="text-xs space-y-1 bg-slate-50 p-3 rounded-lg border border-slate-200 font-mono">
              <div>Issue: <span className="font-bold text-slate-800">{activeIssue.issue_id}</span></div>
              <div>Type: <span className="text-indigo-600 font-bold">{activeIssue.issue_type}</span></div>
              <div>Entity: {activeIssue.entity_id}</div>
            </div>

            <form onSubmit={handleUpdateStatus} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">New Workflow Status</label>
                <select
                  value={newStatus}
                  onChange={(e: any) => setNewStatus(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg p-2 font-medium"
                >
                  <option value="INVESTIGATED">Investigated (Root Cause Identified)</option>
                  <option value="RESOLVED">Resolved (Remediation Applied)</option>
                  <option value="DISMISSED">Dismissed (False Positive / Accepted Exception)</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Documented Remediation Rationale</label>
                <textarea
                  rows={3}
                  required
                  placeholder="Detail the root cause investigation, data remediation steps, or dismissal rationale..."
                  value={rationale}
                  onChange={(e) => setRationale(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg p-2"
                />
              </div>

              <div className="pt-3 border-t border-slate-200 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setActiveIssue(null)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 font-medium hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updating}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 disabled:opacity-50"
                >
                  {updating ? 'Saving...' : 'Update Status & Log Audit'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
