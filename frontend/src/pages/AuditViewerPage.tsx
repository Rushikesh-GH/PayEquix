import React, { useEffect, useState } from 'react';
import { History, Search, ShieldCheck, Filter, ArrowRight } from 'lucide-react';
import { api } from '../services/api';
import { AuditEvent } from '../types';

export const AuditViewerPage: React.FC = () => {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterActor, setFilterActor] = useState('');
  const [filterAction, setFilterAction] = useState('');
  const [selectedEvent, setSelectedEvent] = useState<AuditEvent | null>(null);

  useEffect(() => {
    loadAuditEvents();
  }, [filterActor, filterAction]);

  const loadAuditEvents = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        ...(filterActor ? { actor: filterActor } : {}),
        ...(filterAction ? { action: filterAction } : {}),
      });
      const data = await api.getAuditEvents(params.toString());
      setEvents(data);
    } catch (e) {
      console.error('Failed to load audit events', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-slate-700/60">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white drop-shadow-sm">Immutable Audit Trail</h1>
          <p className="text-sm text-slate-300 mt-1">
            Append-only audit event log recording every state transition, proposal review, and compensation change.
          </p>
        </div>
        <div className="text-xs bg-slate-800/80 text-slate-200 px-3.5 py-1.5 rounded-xl border border-slate-700 font-medium shadow-sm">
          Events Logged: <span className="font-bold text-indigo-400 font-mono">{events.length}</span>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-wrap gap-4 text-xs">
        <div>
          <label className="block text-slate-500 mb-1 font-medium">Actor</label>
          <input
            type="text"
            placeholder="Filter by actor (e.g. hr_lead, admin)..."
            value={filterActor}
            onChange={(e) => setFilterActor(e.target.value)}
            className="border border-slate-300 rounded-lg p-2 min-w-[200px]"
          />
        </div>

        <div>
          <label className="block text-slate-500 mb-1 font-medium">Action</label>
          <select
            value={filterAction}
            onChange={(e) => setFilterAction(e.target.value)}
            className="border border-slate-300 rounded-lg p-2 min-w-[180px]"
          >
            <option value="">All Actions</option>
            <option value="CREATE_PROPOSAL">CREATE_PROPOSAL</option>
            <option value="SUBMIT">SUBMIT</option>
            <option value="APPROVE">APPROVE</option>
            <option value="REJECT">REJECT</option>
            <option value="APPLY_ADJUSTMENT">APPLY_ADJUSTMENT</option>
            <option value="UPDATE_STATUS">UPDATE_STATUS</option>
            <option value="UNAUTHORIZED_APPLY_ATTEMPT">UNAUTHORIZED_APPLY_ATTEMPT</option>
          </select>
        </div>
      </div>

      {/* Audit Events Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Event ID</th>
                <th className="py-3 px-4">Entity</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Actor</th>
                <th className="py-3 px-4">Reason / Notes</th>
                <th className="py-3 px-4">Correlation ID</th>
                <th className="py-3 px-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-2"></div>
                    Loading audit events...
                  </td>
                </tr>
              ) : events.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500">
                    No audit records matching filter criteria.
                  </td>
                </tr>
              ) : (
                events.map((ev) => (
                  <tr key={ev.event_id} className="hover:bg-slate-50">
                    <td className="py-3 px-4 font-mono text-slate-500 text-[11px] whitespace-nowrap">
                      {ev.timestamp.replace('T', ' ').slice(0, 19)}
                    </td>
                    <td className="py-3 px-4 font-mono font-medium text-slate-900">{ev.event_id}</td>
                    <td className="py-3 px-4">
                      <span className="font-semibold text-slate-800">{ev.entity_type}</span>
                      <div className="font-mono text-indigo-600 text-[11px]">{ev.entity_id}</div>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-mono font-semibold ${
                        ev.action.includes('UNAUTHORIZED')
                          ? 'bg-rose-100 text-rose-800'
                          : ev.action.includes('APPLY')
                          ? 'bg-emerald-100 text-emerald-800'
                          : ev.action.includes('APPROVE')
                          ? 'bg-indigo-100 text-indigo-800'
                          : 'bg-slate-100 text-slate-800'
                      }`}>
                        {ev.action}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-900">{ev.actor}</td>
                    <td className="py-3 px-4 max-w-xs truncate text-slate-600">{ev.reason}</td>
                    <td className="py-3 px-4 font-mono text-slate-400 text-[11px]">{ev.correlation_id}</td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => setSelectedEvent(ev)}
                        className="text-indigo-600 hover:text-indigo-900 font-semibold"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* JSON Inspection Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Audit Record Inspector</h3>
            <div className="text-xs space-y-1 bg-slate-50 p-3 rounded-lg border border-slate-200 font-mono">
              <div>Event: <span className="font-bold">{selectedEvent.event_id}</span></div>
              <div>Action: <span className="text-indigo-600 font-bold">{selectedEvent.action}</span></div>
              <div>Actor: {selectedEvent.actor}</div>
              <div>Timestamp: {selectedEvent.timestamp}</div>
              <div>Correlation: {selectedEvent.correlation_id}</div>
            </div>

            <div className="text-xs space-y-2">
              <div>
                <span className="font-semibold text-slate-700">Reason / Description:</span>
                <p className="p-2 bg-slate-50 rounded border border-slate-200 mt-1 text-slate-700">
                  {selectedEvent.reason}
                </p>
              </div>

              {selectedEvent.before_values && (
                <div>
                  <span className="font-semibold text-slate-700">Before Values:</span>
                  <pre className="p-2 bg-slate-900 text-slate-100 rounded text-[11px] overflow-x-auto mt-1">
                    {selectedEvent.before_values}
                  </pre>
                </div>
              )}

              {selectedEvent.after_values && (
                <div>
                  <span className="font-semibold text-slate-700">After Values:</span>
                  <pre className="p-2 bg-slate-900 text-emerald-400 rounded text-[11px] overflow-x-auto mt-1">
                    {selectedEvent.after_values}
                  </pre>
                </div>
              )}
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedEvent(null)}
                className="px-4 py-2 bg-slate-800 text-white rounded-lg text-xs font-semibold hover:bg-slate-900"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
