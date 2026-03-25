'use client';

import { useEffect, useState } from 'react';
import { Plus, Users, Trash2, Eye, Pencil } from 'lucide-react';
import { patientsApi } from '@/lib/api';
import { Patient } from '@/types';
import { formatDate, calcAge } from '@/lib/utils';
import {
  PageLoader, EmptyState, ErrorBanner, SearchInput,
  ConfirmDialog, StatusBadge,
} from '@/components/ui';
import PatientModal from '@/components/patients/PatientModal';
import Link from 'next/link';

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Patient | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Patient | null>(null);
  const [deleting, setDeleting] = useState(false);

  const load = async () => {
    try {
      const data = await patientsApi.list(0, 500);
      setPatients(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filtered = patients.filter(p => {
    const q = search.toLowerCase();
    return (
      `${p.first_name} ${p.last_name}`.toLowerCase().includes(q) ||
      p.email?.toLowerCase().includes(q) ||
      p.phone?.includes(q)
    );
  });

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await patientsApi.delete(deleteTarget.patient_id);
      setPatients(ps => ps.filter(p => p.patient_id !== deleteTarget.patient_id));
      setDeleteTarget(null);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setDeleting(false);
    }
  };

  if (loading) return <PageLoader />;

  return (
    <div className="space-y-4 animate-fade-in-up">
      {error && <ErrorBanner message={error} />}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Patients</h1>
          <p className="text-sm text-slate-500 mt-0.5">{patients.length} registered</p>
        </div>
        <button
          className="btn-primary"
          onClick={() => { setEditing(null); setModalOpen(true); }}
        >
          <Plus className="w-4 h-4" /> New Patient
        </button>
      </div>

      {/* Search */}
      <div className="card px-4 py-3 flex items-center gap-3">
        <SearchInput value={search} onChange={setSearch} placeholder="Search by name, email or phone…" />
        <span className="text-xs text-slate-400 ml-auto">{filtered.length} results</span>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        {filtered.length === 0 ? (
          <EmptyState
            icon={<Users className="w-10 h-10" />}
            title="No patients found"
            description="Register a new patient to get started."
            action={
              <button className="btn-primary" onClick={() => { setEditing(null); setModalOpen(true); }}>
                <Plus className="w-4 h-4" /> New Patient
              </button>
            }
          />
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-100">
              <tr>
                {['Patient', 'Age / DOB', 'Blood Type', 'Contact', 'Emergency Contact', 'Registered', ''].map(h => (
                  <th key={h} className="table-header px-4 py-3 text-left">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {filtered.map(p => (
                <tr key={p.patient_id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center flex-shrink-0">
                        <span className="text-xs font-semibold text-brand-700">
                          {p.first_name[0]}{p.last_name[0]}
                        </span>
                      </div>
                      <div>
                        <Link href={`/patients/${p.patient_id}`} className="font-medium text-slate-900 hover:text-brand-600">
                          {p.first_name} {p.last_name}
                        </Link>
                        <p className="text-xs text-slate-400">{p.gender}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    <span>{calcAge(p.date_of_birth)}</span>
                    <p className="text-xs text-slate-400">{formatDate(p.date_of_birth)}</p>
                  </td>
                  <td className="px-4 py-3">
                    {p.blood_group ? (
                      <span className="badge bg-red-50 text-red-700 ring-red-200">{p.blood_group}</span>
                    ) : '—'}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    <p>{p.phone ?? '—'}</p>
                    <p className="text-xs text-slate-400">{p.email ?? ''}</p>
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    <p>{p.emergency_contact ?? '—'}</p>
                  </td>
                  <td className="px-4 py-3 text-slate-500 text-xs">{formatDate(p.registration_date)}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <Link href={`/patients/${p.patient_id}`}
                        className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-700">
                        <Eye className="w-3.5 h-3.5" />
                      </Link>
                      <button
                        onClick={() => { setEditing(p); setModalOpen(true); }}
                        className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-700">
                        <Pencil className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setDeleteTarget(p)}
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

      <PatientModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        patient={editing}
        onSaved={() => { setModalOpen(false); load(); }}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        loading={deleting}
        title="Delete Patient"
        message={`Are you sure you want to delete ${deleteTarget?.first_name} ${deleteTarget?.last_name}? This action cannot be undone.`}
      />
    </div>
  );
}
