'use client';

import { useEffect, useState } from 'react';
import { Plus, CalendarDays, Pencil, Trash2 } from 'lucide-react';
import { appointmentsApi } from '@/lib/api';
import { Appointment, AppointmentStatus } from '@/types';
import { formatDate } from '@/lib/utils';
import { PageLoader, EmptyState, ErrorBanner, SearchInput, ConfirmDialog, StatusBadge } from '@/components/ui';
import AppointmentModal from '@/components/appointments/AppointmentModal';

const STATUSES: AppointmentStatus[] = ['Scheduled', 'Completed', 'Cancelled', 'No-Show'];

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Appointment | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Appointment | null>(null);
  const [deleting, setDeleting] = useState(false);

  const load = async () => {
    try { setAppointments(await appointmentsApi.list(0, 500)); }
    catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const filtered = appointments.filter(a => {
    const q = search.toLowerCase();
    const matchSearch = !q ||
      `${a.patient?.first_name} ${a.patient?.last_name}`.toLowerCase().includes(q) ||
      `${a.doctor?.first_name} ${a.doctor?.last_name}`.toLowerCase().includes(q) ||
      a.reason?.toLowerCase().includes(q);
    const matchStatus = !statusFilter || a.status === statusFilter;
    return matchSearch && matchStatus;
  });

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await appointmentsApi.delete(deleteTarget.appointment_id);
      setAppointments(as => as.filter(a => a.appointment_id !== deleteTarget.appointment_id));
      setDeleteTarget(null);
    } catch (e: any) { setError(e.message); }
    finally { setDeleting(false); }
  };

  const handleStatusChange = async (id: number, status: string) => {
    try {
      await appointmentsApi.updateStatus(id, status);
      setAppointments(as => as.map(a => a.appointment_id === id ? { ...a, status: status as AppointmentStatus } : a));
    } catch (e: any) { setError(e.message); }
  };

  if (loading) return <PageLoader />;

  // Group by date
  const sorted = [...filtered].sort((a, b) =>
    `${b.appointment_date}${b.appointment_time}`.localeCompare(`${a.appointment_date}${a.appointment_time}`)
  );

  return (
    <div className="space-y-4 animate-fade-in-up">
      {error && <ErrorBanner message={error} />}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Appointments</h1>
          <p className="text-sm text-slate-500 mt-0.5">{appointments.length} total</p>
        </div>
        <button className="btn-primary" onClick={() => { setEditing(null); setModalOpen(true); }}>
          <Plus className="w-4 h-4" /> Book Appointment
        </button>
      </div>

      {/* Filters */}
      <div className="card px-4 py-3 flex items-center gap-3 flex-wrap">
        <SearchInput value={search} onChange={setSearch} placeholder="Search patient, doctor or reason…" />
        <div className="flex gap-1.5">
          <button
            className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${!statusFilter ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
            onClick={() => setStatusFilter('')}
          >All</button>
          {STATUSES.map(s => (
            <button key={s}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${statusFilter === s ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
              onClick={() => setStatusFilter(s === statusFilter ? '' : s)}
            >{s}</button>
          ))}
        </div>
        <span className="text-xs text-slate-400 ml-auto">{filtered.length} results</span>
      </div>

      <div className="card overflow-hidden">
        {sorted.length === 0 ? (
          <EmptyState
            icon={<CalendarDays className="w-10 h-10" />}
            title="No appointments found"
            action={<button className="btn-primary" onClick={() => { setEditing(null); setModalOpen(true); }}><Plus className="w-4 h-4" /> Book Appointment</button>}
          />
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-100">
              <tr>
                {['Patient', 'Doctor', 'Date & Time', 'Reason', 'Status', ''].map(h => (
                  <th key={h} className="table-header px-4 py-3 text-left">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {sorted.map(a => (
                <tr key={a.appointment_id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="px-4 py-3 font-medium text-slate-800">
                    {a.patient ? `${a.patient.first_name} ${a.patient.last_name}` : `#${a.patient_id}`}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {a.doctor ? `Dr. ${a.doctor.first_name} ${a.doctor.last_name}` : `#${a.doctor_id}`}
                    {a.doctor && <p className="text-xs text-slate-400">{a.doctor.specialization}</p>}
                  </td>
                  <td className="px-4 py-3">
                    <p className="text-slate-800">{formatDate(a.appointment_date)}</p>
                    <p className="text-xs text-slate-400">{a.appointment_time?.slice(0, 5)}</p>
                  </td>
                  <td className="px-4 py-3 text-slate-500 max-w-[180px] truncate">{a.reason ?? '—'}</td>
                  <td className="px-4 py-3">
                    <select
                      value={a.status}
                      onChange={e => handleStatusChange(a.appointment_id, e.target.value)}
                      className="text-xs border border-slate-200 rounded-lg px-2 py-1 bg-white focus:outline-none focus:ring-1 focus:ring-brand-500"
                    >
                      {STATUSES.map(s => <option key={s}>{s}</option>)}
                    </select>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <button onClick={() => { setEditing(a); setModalOpen(true); }}
                        className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-700">
                        <Pencil className="w-3.5 h-3.5" />
                      </button>
                      <button onClick={() => setDeleteTarget(a)}
                        className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-red-50 hover:text-red-600">
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <AppointmentModal open={modalOpen} onClose={() => setModalOpen(false)} appointment={editing} onSaved={() => { setModalOpen(false); load(); }} />
      <ConfirmDialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={handleDelete} loading={deleting}
        title="Cancel Appointment" message="Are you sure you want to delete this appointment?" />
    </div>
  );
}
