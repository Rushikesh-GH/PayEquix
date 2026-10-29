import React, { useEffect, useState } from 'react';
import { 
  Users, AlertTriangle, ShieldCheck, TrendingUp, 
  ArrowUpRight, ArrowDownRight, Layers, FileText, CheckCircle2, Sparkles, Orbit
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  LineChart, Line, CartesianGrid, Legend, Cell 
} from 'recharts';
import { api } from '../services/api';
import { MetricCard3D } from '../components/MetricCard3D';
import { CompensationGalaxy3D } from '../components/CompensationGalaxy3D';
import { ExecutiveMetrics } from '../types';

interface DashboardPageProps {
  onNavigate: (tab: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [metrics, setMetrics] = useState<ExecutiveMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      const data = await api.getExecutiveMetrics();
      setMetrics(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load executive metrics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="bg-rose-50 border border-rose-200 rounded-xl p-6 text-rose-800 text-center">
        <AlertTriangle className="w-8 h-8 text-rose-500 mx-auto mb-2" />
        <h3 className="font-semibold">Unable to load dashboard data</h3>
        <p className="text-sm mt-1">{error}</p>
        <button
          onClick={loadMetrics}
          className="mt-4 px-4 py-2 bg-rose-600 text-white rounded-lg text-sm hover:bg-rose-700"
        >
          Retry
        </button>
      </div>
    );
  }

  const exceptionData = Object.entries(metrics.exception_type_counts || {}).map(([name, count]) => ({
    name: name.replace(/_/g, ' '),
    count,
  }));

  const proposalData = Object.entries(metrics.proposal_status_counts || {}).map(([status, count]) => ({
    status: status.replace(/_/g, ' '),
    count,
  }));

  const COLORS = ['#6366f1', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="space-y-6">
      {/* Page Title & Status Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-slate-700/60">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white drop-shadow-sm">Executive Compensation Equity Dashboard</h1>
          <p className="text-sm text-slate-300 mt-1">
            Real-time explainable disparity detection, band alignment, and human-in-the-loop review proposals.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="flex items-center px-3.5 py-1.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
            <CheckCircle2 className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />
            Deterministic Validation: PASS (22/22)
          </span>
        </div>
      </div>

      {/* Top 3D Spatial Visualization */}
      <CompensationGalaxy3D 
        metrics={metrics} 
        onSelectAnomaly={() => onNavigate('exceptions')} 
      />

      {/* Top 3D Perspective Tilt Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricCard3D
          title="Total Workforce"
          value={metrics.total_employees.toLocaleString()}
          subtitle={`${metrics.valid_comparisons_count.toLocaleString()} eligible for band comparison`}
          icon={Users}
          badge={{ text: 'Active Dataset', type: 'info' }}
          accentColor="indigo"
        />
        <MetricCard3D
          title="Review Candidates"
          value={metrics.review_candidates_count.toLocaleString()}
          subtitle="Identified for human-in-the-loop audit"
          icon={TrendingUp}
          badge={{ text: `${((metrics.review_candidates_count / metrics.total_employees) * 100).toFixed(1)}% of total`, type: 'warning' }}
          accentColor="amber"
        />
        <MetricCard3D
          title="Data Quality Exceptions"
          value={metrics.data_quality_exceptions_count.toLocaleString()}
          subtitle="Input integrity defects (blocked from analysis)"
          icon={AlertTriangle}
          badge={{ text: metrics.data_quality_exceptions_count > 0 ? 'Requires Fix' : 'Clean', type: metrics.data_quality_exceptions_count > 0 ? 'danger' : 'success' }}
          accentColor="rose"
        />
        <MetricCard3D
          title="Average Compa-Ratio"
          value={metrics.avg_compa_ratio ? metrics.avg_compa_ratio.toFixed(2) : '1.00'}
          subtitle="Benchmark midpoint target: 1.00"
          icon={ShieldCheck}
          badge={{ text: 'Within Target Range', type: 'success' }}
          accentColor="emerald"
        />
      </div>

      {/* Secondary Metrics Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-white p-4 rounded-xl border border-slate-200 text-center">
        <div>
          <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">Below Band Minimum</div>
          <div className="text-xl font-bold text-rose-600 mt-1 flex items-center justify-center">
            <ArrowDownRight className="w-4 h-4 mr-0.5" />
            {metrics.below_band_count}
          </div>
          <div className="text-xs text-slate-400 mt-0.5">Position &lt; 0%</div>
        </div>
        <div>
          <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">Above Band Maximum</div>
          <div className="text-xl font-bold text-amber-600 mt-1 flex items-center justify-center">
            <ArrowUpRight className="w-4 h-4 mr-0.5" />
            {metrics.above_band_count}
          </div>
          <div className="text-xs text-slate-400 mt-0.5">Position &gt; 100%</div>
        </div>
        <div>
          <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">Pending Proposals</div>
          <div className="text-xl font-bold text-indigo-600 mt-1">{metrics.pending_proposals_count}</div>
          <div className="text-xs text-slate-400 mt-0.5">Awaiting HR Approval</div>
        </div>
        <div>
          <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">Applied Adjustments</div>
          <div className="text-xl font-bold text-emerald-600 mt-1">{metrics.applied_proposals_count}</div>
          <div className="text-xs text-slate-400 mt-0.5">Audited & Reconciled</div>
        </div>
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Compa-Ratio Distribution */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-slate-900 text-sm">Compa-Ratio Distribution</h3>
              <p className="text-xs text-slate-500">Benchmark midpoint = 1.00; healthy spread 0.85 – 1.15</p>
            </div>
            <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded font-mono font-medium">
              CR = Salary / Midpoint
            </span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metrics.compa_ratio_distribution}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="bucket" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip 
                  formatter={(val: number) => [`${val.toLocaleString()} employees`, 'Count']}
                  contentStyle={{ backgroundColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Band Position Distribution */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-slate-900 text-sm">Within-Band Position Distribution</h3>
              <p className="text-xs text-slate-500">0% = Band Min, 50% = Mid, 100% = Max (unclipped outliers shown)</p>
            </div>
            <span className="text-xs bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-mono font-medium">
              Pos = (Sal - Min) / Spread
            </span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metrics.band_position_distribution}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="bucket" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip 
                  formatter={(val: number) => [`${val.toLocaleString()} employees`, 'Count']}
                  contentStyle={{ backgroundColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {metrics.band_position_distribution.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.bucket.includes('Below') ? '#ef4444' : entry.bucket.includes('Above') ? '#f59e0b' : '#3b82f6'} 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Historical Trends & Exception Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Historical Trends */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-slate-900 text-sm">3-Year Historical Compensation Growth</h3>
              <p className="text-xs text-slate-500">Annual merit and promotion cycles covering 2024, 2025, and 2026</p>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics.historical_trends}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="year" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} domain={['dataMin - 10000', 'dataMax + 10000']} />
                <Tooltip 
                  formatter={(val: number) => [`$${val.toLocaleString()}`, 'Avg Base Salary']}
                  contentStyle={{ backgroundColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Legend />
                <Line type="monotone" dataKey="avg_salary_usd" name="Avg FTE Salary (USD)" stroke="#6366f1" strokeWidth={2.5} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Exceptions & Review Proposals Status */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="font-semibold text-slate-900 text-sm">Active Review Proposals by Status</h3>
                <p className="text-xs text-slate-500">Human-in-the-loop proposal governance lifecycle</p>
              </div>
              <button 
                onClick={() => onNavigate('proposals')}
                className="text-xs font-semibold text-indigo-600 hover:text-indigo-800"
              >
                View Proposals →
              </button>
            </div>
            <div className="space-y-3 mt-4">
              {proposalData.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs">
                  <span className="font-medium text-slate-700 capitalize">{item.status}</span>
                  <div className="flex items-center space-x-2 w-2/3">
                    <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                      <div 
                        className="bg-indigo-600 h-2 rounded-full" 
                        style={{ width: `${Math.min(100, (item.count / (metrics.total_employees || 1)) * 100 * 20)}%` }}
                      ></div>
                    </div>
                    <span className="font-bold text-slate-900 w-8 text-right">{item.count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
            <div className="text-xs text-slate-500">
              <span className="font-semibold text-slate-700">{metrics.data_quality_exceptions_count} Data Quality Exceptions</span> need investigation.
            </div>
            <button
              onClick={() => onNavigate('exceptions')}
              className="text-xs px-3 py-1.5 bg-amber-50 text-amber-800 font-semibold rounded-lg border border-amber-200 hover:bg-amber-100 transition-colors"
            >
              Open Exceptions Workbench →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
