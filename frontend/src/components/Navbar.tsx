import React from 'react';
import { 
  BarChart3, Users, AlertTriangle, FileText, 
  Layers, ShieldCheck, History, UserCheck, Sparkles 
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  currentUser: { username: string; role: string; fullName: string };
  onSwitchUser: (username: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  currentUser,
  onSwitchUser,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Executive Dashboard', icon: BarChart3 },
    { id: 'employees', label: 'Employee Explorer', icon: Users },
    { id: 'exceptions', label: 'Exceptions Workbench', icon: AlertTriangle },
    { id: 'proposals', label: 'Review Proposals', icon: FileText },
    { id: 'groups', label: 'Comparable Groups', icon: Layers },
    { id: 'data-quality', label: 'Data Quality & Evaluation', icon: ShieldCheck },
    { id: 'audit', label: 'Audit Viewer', icon: History },
  ];

  const demoUsers = [
    { username: 'admin', role: 'system_admin', label: 'Admin (System Administrator)' },
    { username: 'hr_lead', role: 'hr_partner', label: 'HR Lead (HR Partner)' },
    { username: 'dept_manager', role: 'manager', label: 'Dept Manager (Manager)' },
    { username: 'auditor', role: 'it_operations', label: 'Auditor (IT Operations)' },
    { username: 'employee1', role: 'employee', label: 'Employee 1 (Staff)' },
  ];

  return (
    <header className="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-30 shadow-lg">
      {/* Synthetic Benchmark Indicator Banner */}
      <div className="bg-indigo-950/80 border-b border-indigo-800/40 text-indigo-200 text-xs px-4 py-1.5 flex items-center justify-between font-mono">
        <div className="flex items-center space-x-2">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="font-semibold text-white">BENCHMARK EVALUATION ENVIRONMENT</span>
          <span>•</span>
          <span>SEED: 20261022</span>
          <span>•</span>
          <span>5,000 SYNTHETIC EMPLOYEES</span>
          <span>•</span>
          <span className="text-indigo-300">FICTIONAL DATA ONLY — NO REAL PII</span>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          <span className="bg-indigo-900/90 border border-indigo-700/50 px-2 py-0.5 rounded text-indigo-200">Non-Adverse AI Guardrails Active</span>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3 cursor-pointer group" onClick={() => setActiveTab('dashboard')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center text-white shadow-lg shadow-indigo-500/25 group-hover:scale-105 transition-transform">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
                Pay<span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">Equix</span>
              </div>
              <div className="text-xs text-slate-400 font-medium">Explainable Pay Equity & Disparity Review System</div>
            </div>
          </div>

          {/* User Role Switcher */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-700/80 text-xs shadow-inner">
              <UserCheck className="w-4 h-4 text-indigo-400 mr-2" />
              <span className="text-slate-400 mr-1.5 font-medium">Actor:</span>
              <select
                value={currentUser.username}
                onChange={(e) => onSwitchUser(e.target.value)}
                className="bg-transparent font-semibold text-slate-200 focus:outline-hidden cursor-pointer"
              >
                {demoUsers.map((u) => (
                  <option key={u.username} value={u.username} className="bg-slate-900 text-slate-100">
                    {u.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="text-xs px-2.5 py-1 rounded-full font-medium uppercase tracking-wider bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
              {currentUser.role.replace('_', ' ')}
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 overflow-x-auto pb-1 text-sm font-medium">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center space-x-2 px-3.5 py-2.5 border-b-2 transition-all whitespace-nowrap ${
                  isActive
                    ? 'border-indigo-400 text-indigo-300 font-semibold bg-indigo-500/10 rounded-t-lg'
                    : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
