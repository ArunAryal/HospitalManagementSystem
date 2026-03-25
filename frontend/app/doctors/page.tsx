'use client';

import { useEffect, useState } from 'react';
import { Plus, UserRound, Pencil, Trash2 } from 'lucide-react';
import { doctorsApi } from '@/lib/api';
import { Doctor } from '@/types';
import { formatDate } from '@/lib/utils';
import { PageLoader, EmptyState, ErrorBanner, SearchInput, ConfirmDialog } from '@/components/ui';
import DoctorModal from '@/components/doctors/DoctorModal';

export default function DoctorsPage() {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Doctor | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Doctor | null>(null);
  const [deleting, setDeleting] = useState(false);

  const load = async () => {
    try { setDoctors(await doctorsApi.list(0, 500)); }
    catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const filtered = doctors.filter(d => {
    const q = search.toLowerCase();
    return `${d.first_name} ${d.last_name}`.toLowerCase().includes(q) ||
      d.specialization.toLowerCase().includes(q) ||
      d.email?.toLowerCase().includes(q);
  });

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await doctorsApi.delete(deleteTarget.doctor_id);
      setDoctors(ds => ds.filter(d => d.doctor_id !== deleteTarget.doctor_id));
      setDeleteTarget(null);
    } catch (e: any) { setError(e.message); }
    finally { setDeleting(false); }
  };

  if (loading) return <PageLoader />;

  const specializations = [...new Set(doctors.map(d => d.specialization))];

  return (
    <div className="space-y-4 animate-fade-in-up">
      {error && <ErrorBanner message={error} />}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Doctors</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {doctors.filter(d => d.is_available).length} of {doctors.length} available
          </p>
        </div>
        <button className="btn-primary" onClick={() => { setEditing(null); setModalOpen(true); }}>
          <Plus className="w-4 h-4" /> Add Doctor
        </button>
      </div>

      <div className="card px-4 py-3 flex items-center gap-3 flex-wrap">
        <SearchInput value={search} onChange={setSearch} placeholder="Search by name or specialization…" />
        <span className="text-xs text-slate-400 ml-auto">{filtered.length} results</span>
      </div>

      {/* Cards grid */}
      {filtered.length === 0 ? (
        <div className="card">
          <EmptyState
            icon={<UserRound className="w-10 h-10" />}
            title="No doctors found"
            action={<button className="btn-primary" onClick={() => { setEditing(null); setModalOpen(true); }}><Plus className="w-4 h-4" /> Add Doctor</button>}
          />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map(d => (
            <div key={d.doctor_id} className="card p-5 flex flex-col gap-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold text-purple-700">{d.first_name[0]}{d.last_name[0]}</span>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">Dr. {d.first_name} {d.last_name}</p>
                    <p className="text-xs text-slate-500">{d.specialization}</p>
                  </div>
                </div>
                <span className={`badge text-xs ${d.is_available ? 'bg-emerald-50 text-emerald-700 ring-emerald-200' : 'bg-slate-100 text-slate-500 ring-slate-200'}`}>
                  {d.is_available ? 'Available' : 'Unavailable'}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <p className="text-slate-400">Specialization</p>
                  <p className="text-slate-700 font-medium mt-0.5">{d.specialization}</p>
                </div>
                <div>
                  <p className="text-slate-400">Joined</p>
                  <p className="text-slate-700 font-medium mt-0.5">{formatDate(d.joined_date)}</p>
                </div>
                {d.phone && <div>
                  <p className="text-slate-400">Phone</p>
                  <p className="text-slate-700 font-medium mt-0.5">{d.phone}</p>
                </div>}
                {d.email && <div>
                  <p className="text-slate-400">Email</p>
                  <p className="text-slate-700 font-medium mt-0.5 truncate">{d.email}</p>
                </div>}
              </div>
              <div className="flex items-center gap-2 pt-2 border-t border-slate-100">
                <button className="btn-secondary text-xs py-1.5 flex-1" onClick={() => { setEditing(d); setModalOpen(true); }}>
                  <Pencil className="w-3 h-3" /> Edit
                </button>
                <button className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-red-50 hover:text-red-600"
                  onClick={() => setDeleteTarget(d)}>
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <DoctorModal open={modalOpen} onClose={() => setModalOpen(false)} doctor={editing} onSaved={() => { setModalOpen(false); load(); }} />
      <ConfirmDialog
        open={!!deleteTarget} onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete} loading={deleting}
        title="Remove Doctor"
        message={`Remove Dr. ${deleteTarget?.first_name} ${deleteTarget?.last_name}?`}
      />
    </div>
  );
}
