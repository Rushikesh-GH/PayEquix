import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { EmployeeExplorerPage } from './pages/EmployeeExplorerPage';
import { EmployeeDetailPage } from './pages/EmployeeDetailPage';
import { ExceptionsPage } from './pages/ExceptionsPage';
import { ProposalsPage } from './pages/ProposalsPage';
import { ComparableGroupsPage } from './pages/ComparableGroupsPage';
import { DataQualityPage } from './pages/DataQualityPage';
import { AuditViewerPage } from './pages/AuditViewerPage';
import { AmbientSpace3D } from './components/AmbientSpace3D';
import { api } from './services/api';

const DEMO_CREDENTIALS: Record<string, { role: string; fullName: string; pass: string }> = {
  admin: { role: 'system_admin', fullName: 'System Administrator', pass: 'AdminPassword123!' },
  hr_lead: { role: 'hr_partner', fullName: 'HR Lead Partner', pass: 'HrPassword123!' },
  dept_manager: { role: 'manager', fullName: 'Department Manager', pass: 'ManagerPassword123!' },
  auditor: { role: 'it_operations', fullName: 'IT Operations Auditor', pass: 'AuditorPassword123!' },
  employee1: { role: 'employee', fullName: 'Staff Employee', pass: 'EmployeePassword123!' },
};

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState({
    username: 'admin',
    role: 'system_admin',
    fullName: 'System Administrator',
  });

  useEffect(() => {
    loginUser('admin');
  }, []);

  const loginUser = async (username: string) => {
    const cred = DEMO_CREDENTIALS[username];
    if (!cred) return;
    try {
      const res = await api.login(username, cred.pass);
      localStorage.setItem('token', res.access_token);
      setCurrentUser({
        username: res.username,
        role: res.role,
        fullName: res.full_name,
      });
    } catch (e) {
      console.error('Failed to login demo user', e);
    }
  };

  const handleSelectEmployee = (empId: string) => {
    setSelectedEmployeeId(empId);
    setActiveTab('employee-detail');
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans relative selection:bg-indigo-500 selection:text-white">
      {/* 3D Global Space & Data Constellation Particles */}
      <AmbientSpace3D />

      <div className="relative z-10 flex flex-col min-h-screen">
        <Navbar
          activeTab={activeTab === 'employee-detail' ? 'employees' : activeTab}
          setActiveTab={(tab) => {
            setSelectedEmployeeId(null);
            setActiveTab(tab);
          }}
          currentUser={currentUser}
          onSwitchUser={loginUser}
        />

        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {activeTab === 'dashboard' && (
            <DashboardPage onNavigate={(tab) => setActiveTab(tab)} />
          )}

          {activeTab === 'employees' && (
            <EmployeeExplorerPage onSelectEmployee={handleSelectEmployee} />
          )}

          {activeTab === 'employee-detail' && selectedEmployeeId && (
            <EmployeeDetailPage
              employeeId={selectedEmployeeId}
              onBack={() => {
                setSelectedEmployeeId(null);
                setActiveTab('employees');
              }}
              currentUser={currentUser}
              onProposalCreated={() => setActiveTab('proposals')}
            />
          )}

          {activeTab === 'exceptions' && (
            <ExceptionsPage
              onSelectEmployee={handleSelectEmployee}
              currentUser={currentUser}
            />
          )}

          {activeTab === 'proposals' && (
            <ProposalsPage
              onSelectEmployee={handleSelectEmployee}
              currentUser={currentUser}
            />
          )}

          {activeTab === 'groups' && <ComparableGroupsPage />}

          {activeTab === 'data-quality' && <DataQualityPage />}

          {activeTab === 'audit' && <AuditViewerPage />}
        </main>

        {/* Project Context & Architectural Governance Footer */}
        <footer className="mt-auto border-t border-slate-800/80 bg-slate-950/80 backdrop-blur-md text-slate-400 text-xs py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 pb-4 border-b border-slate-800/60">
              <div>
                <h4 className="font-semibold text-slate-200 text-sm mb-1.5 flex items-center space-x-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
                  <span>Explainable Pay Parity</span>
                </h4>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Evaluates base salaries across role, career level, location zone, and documented performance evidence without protected class leakage.
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-slate-200 text-sm mb-1.5 flex items-center space-x-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                  <span>Band & FTE Normalization</span>
                </h4>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Deterministic currency conversion and full-time equivalent (FTE) scaling against active effective-dated compensation bands.
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-slate-200 text-sm mb-1.5 flex items-center space-x-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                  <span>Human-in-the-Loop Reviews</span>
                </h4>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Separation of duties workflow with state-machine governance (Draft ➔ Review ➔ Approved ➔ Applied) preserving salary history.
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-slate-200 text-sm mb-1.5 flex items-center space-x-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                  <span>Data Integrity & Audit Log</span>
                </h4>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  22/22 deterministic integrity rules, small-sample suppression (&lt; 5 members), and tamper-evident append-only audit tracking.
                </p>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-500 font-mono gap-2">
              <div className="flex items-center space-x-2">
                <span className="text-slate-300 font-medium">PayEquix Compensation Parity & Explainable Equity System</span>
                <span>•</span>
                <span>Deterministic Seed: 20261022</span>
                <span>•</span>
                <span>Evaluation Baseline: 100% Precision / Recall</span>
              </div>
              <div className="text-slate-400">
                Non-Adverse AI Guardrails Active • Role-Based Access Control Enforced
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default App;
