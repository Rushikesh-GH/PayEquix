import React, { useEffect, useState } from 'react';
import { 
  Search, Filter, ArrowUpDown, ChevronLeft, ChevronRight, 
  ExternalLink, AlertCircle, CheckCircle, HelpCircle 
} from 'lucide-react';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { Role, Level, Location } from '../types';

interface EmployeeExplorerProps {
  onSelectEmployee: (employeeId: string) => void;
}

export const EmployeeExplorerPage: React.FC<EmployeeExplorerProps> = ({ onSelectEmployee }) => {
  const [employees, setEmployees] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('active');

  // Master dropdown data
  const [roles, setRoles] = useState<Role[]>([]);
  const [levels, setLevels] = useState<Level[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);

  useEffect(() => {
    loadMasterData();
  }, []);

  useEffect(() => {
    loadEmployees();
  }, [page, pageSize, selectedRole, selectedLevel, selectedLocation, selectedStatus]);

  const loadMasterData = async () => {
    try {
      const [r, l, loc] = await Promise.all([
        api.getRoles(),
        api.getLevels(),
        api.getLocations(),
      ]);
      setRoles(r);
      setLevels(l);
      setLocations(loc);
    } catch (e) {
      console.error('Failed to load master filter data', e);
    }
  };

  const loadEmployees = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        ...(search ? { search } : {}),
        ...(selectedRole ? { role_id: selectedRole } : {}),
        ...(selectedLevel ? { level_id: selectedLevel } : {}),
        ...(selectedLocation ? { location_id: selectedLocation } : {}),
        ...(selectedStatus ? { status: selectedStatus } : {}),
      });

      const res = await api.getEmployees(params.toString());
      setEmployees(res.items || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (e) {
      console.error('Failed to load employees', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadEmployees();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-slate-700/60">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white drop-shadow-sm">Employee Explorer</h1>
          <p className="text-sm text-slate-300 mt-1">
            Search, filter, and inspect compensation parity metrics across 5,000 workforce records.
          </p>
        </div>
        <div className="text-sm font-semibold text-slate-200 bg-slate-800/80 px-3.5 py-1.5 rounded-xl border border-slate-700 shadow-sm">
          Total Matched: <span className="text-indigo-400 font-mono font-bold">{total.toLocaleString()}</span>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search by Employee ID (EMP-000001), code, or synthetic name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-hidden focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
          >
            Search
          </button>
        </form>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div>
            <label className="block text-slate-700 mb-1 font-semibold">Job Role</label>
            <select
              value={selectedRole}
              onChange={(e) => { setSelectedRole(e.target.value); setPage(1); }}
              className="w-full border border-slate-300 rounded-lg p-2 bg-white text-slate-900 font-medium focus:ring-2 focus:ring-indigo-500 shadow-xs"
            >
              <option value="" className="text-slate-900 bg-white">All Roles (25)</option>
              {roles.map((r) => (
                <option key={r.role_id} value={r.role_id} className="text-slate-900 bg-white">{r.role_name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-700 mb-1 font-semibold">Career Level</label>
            <select
              value={selectedLevel}
              onChange={(e) => { setSelectedLevel(e.target.value); setPage(1); }}
              className="w-full border border-slate-300 rounded-lg p-2 bg-white text-slate-900 font-medium focus:ring-2 focus:ring-indigo-500 shadow-xs"
            >
              <option value="" className="text-slate-900 bg-white">All Levels (8)</option>
              {levels.map((l) => (
                <option key={l.level_id} value={l.level_id} className="text-slate-900 bg-white">{l.level_name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-700 mb-1 font-semibold">Location</label>
            <select
              value={selectedLocation}
              onChange={(e) => { setSelectedLocation(e.target.value); setPage(1); }}
              className="w-full border border-slate-300 rounded-lg p-2 bg-white text-slate-900 font-medium focus:ring-2 focus:ring-indigo-500 shadow-xs"
            >
              <option value="" className="text-slate-900 bg-white">All Locations (10)</option>
              {locations.map((loc) => (
                <option key={loc.location_id} value={loc.location_id} className="text-slate-900 bg-white">{loc.city}, {loc.country}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-700 mb-1 font-semibold">Status</label>
            <select
              value={selectedStatus}
              onChange={(e) => { setSelectedStatus(e.target.value); setPage(1); }}
              className="w-full border border-slate-300 rounded-lg p-2 bg-white text-slate-900 font-medium focus:ring-2 focus:ring-indigo-500 shadow-xs"
            >
              <option value="" className="text-slate-900 bg-white">All Statuses</option>
              <option value="active" className="text-slate-900 bg-white">Active</option>
              <option value="on_leave" className="text-slate-900 bg-white">On Leave</option>
              <option value="terminated" className="text-slate-900 bg-white">Terminated</option>
            </select>
          </div>
        </div>
      </div>

      {/* Employees Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Employee</th>
                <th className="py-3 px-4">Role & Level</th>
                <th className="py-3 px-4">Location</th>
                <th className="py-3 px-4">Type & FTE</th>
                <th className="py-3 px-4">Hire Date</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-2"></div>
                    Loading employees...
                  </td>
                </tr>
              ) : employees.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    No employees matching filter criteria found.
                  </td>
                </tr>
              ) : (
                employees.map((emp) => (
                  <tr 
                    key={emp.employee_id} 
                    className="hover:bg-slate-50 transition-colors cursor-pointer"
                    onClick={() => onSelectEmployee(emp.employee_id)}
                  >
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-slate-900">{emp.first_name} {emp.last_name}</div>
                      <div className="font-mono text-indigo-600 text-[11px]">{emp.employee_id}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-medium text-slate-800">{emp.role_name}</div>
                      <div className="text-slate-500 text-[11px]">{emp.level_name}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="text-slate-800">{emp.location_name}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="capitalize">{emp.employment_type.replace('_', ' ')}</span>
                      <span className="ml-1 text-slate-500 font-mono">({(emp.fte * 100).toFixed(0)}%)</span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-600">{emp.hire_date}</td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={emp.employment_status} />
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectEmployee(emp.employee_id);
                        }}
                        className="text-indigo-600 hover:text-indigo-900 font-semibold inline-flex items-center space-x-1"
                      >
                        <span>Analyze</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 border-t border-slate-200 flex items-center justify-between text-xs text-slate-600">
          <div>
            Showing <span className="font-semibold">{employees.length ? (page - 1) * pageSize + 1 : 0}</span> to{' '}
            <span className="font-semibold">{Math.min(page * pageSize, total)}</span> of{' '}
            <span className="font-semibold">{total.toLocaleString()}</span> employees
          </div>

          <div className="flex items-center space-x-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              className="p-1.5 border border-slate-300 rounded-lg hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-medium">
              Page {page} of {totalPages}
            </span>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage(page + 1)}
              className="p-1.5 border border-slate-300 rounded-lg hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
