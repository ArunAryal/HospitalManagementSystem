'use client';

import { useEffect, useState } from 'react';
import { Plus, FileText, Pencil, Trash2, ChevronDown, ChevronUp } from 'lucide-react';
import { medicalRecordsApi } from '@/lib/api';
import { MedicalRecord } from '@/types';
import { formatDate } from '@/lib/utils';
import { PageLoader, EmptyState, ErrorBanner, SearchInput, ConfirmDialog } from '@/components/ui';
import MedicalRecordModal from '@/components/medical-records/MedicalRecordModal';
import PrescriptionPanel from '@/components/medical-records/PrescriptionPanel';

export default function MedicalRecordsPage() {
  const [records, setRecords] = useState<MedicalRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<MedicalRecord | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<MedicalRecord | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [expanded, setExpanded] = useState<number | null>(null);

  const load = async () => {
    try { setRecords(await medicalRecordsApi.list(0, 500)); }
    catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const filtered = records.filter(r => {
    const q = search.toLowerCase();
    return r.diagnosis.toLowerCase().includes(q) ||
      `${(r as any).patient?.first_name} ${(r as any).patient?.last_name}`.toLowerCase().includes(q) ||
      r.treatment?.toLowerCase().includes(q);
  });

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await medicalRecordsApi.delete(deleteTarget.record_id);
      setRecords(rs => rs.filter(r => r.record_id !== deleteTarget.record_id));
      setDeleteTarget(null);
    } catch (e: any) { setError(e.message); }
    finally { setDeleting(false); }
  };

  if (loading) return <PageLoader />;

  return (
    <div className="space-y-4 animate-fade-in-up">
      {error && <ErrorBanner message={error} />}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Medical Records</h1>
          <p className="text-sm text-slate-500 mt-0.5">{records.length} records</p>
        </div>
        <button className="btn-primary" onClick={() => { setEditing(null); setModalOpen(true); }}>
          <Plus className="w-4 h-4" /> New Record
        </button>
      </div>

      <div className="card px-4 py-3 flex items-center gap-3">
        <SearchInput value={search} onChange={setSearch} placeholder="Search by diagnosis, patient…" />
        <span className="text-xs text-slate-400 ml-auto">{filtered.length} results</span>
      </div>

      <div className="card overflow-hidden">
        {filtered.length === 0 ? (
          <EmptyState icon={<FileText className="w-10 h-10" />} title="No medical records found"
            action={<button className="btn-primary" onClick={() => { setEditing(null); setModalOpen(true); }}><Plus className="w-4 h-4" /> New Record</button>} />
        ) : (
          <div className="divide-y divide-slate-100">
            {filtered.map(r => {
              const rec = r as any;
              const isOpen = expanded === r.record_id;
              return (
                <div key={r.record_id}>
                  <div className="flex items-start gap-4 px-5 py-4 hover:bg-slate-50/60 transition-colors">
                    <div className="w-9 h-9 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <FileText className="w-4 h-4 text-brand-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="text-sm font-semibold text-slate-900">{r.diagnosis}</p>
                          <p className="text-xs text-slate-500 mt-0.5">
                            {rec.patient ? `${rec.patient.first_name} ${rec.patient.last_name}` : `Patient #${r.patient_id}`}
                            {' · '}
                            {rec.doctor ? `Dr. ${rec.doctor.first_name} ${rec.doctor.last_name}` : `Doctor #${r.doctor_id}`}
                            {' · '}
                            {formatDate(r.record_date)}
                          </p>
                        </div>
                        <div className="flex items-center gap-1 flex-shrink-0">
                          <button onClick={() => setExpanded(isOpen ? null : r.record_id)}
                            className="flex items-center gap-1 px-2 py-1 text-xs text-brand-600 hover:bg-brand-50 rounded-lg transition-colors">
                            Details {isOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                          </button>
                          <button onClick={() => { setEditing(r); setModalOpen(true); }}
                            className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100">
                            <Pencil className="w-3.5 h-3.5" />
                          </button>
                          <button onClick={() => setDeleteTarget(r)}
                            className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-red-50 hover:text-red-600">
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                      {r.notes && <p className="text-xs text-slate-400 mt-1 italic">"{r.notes}"</p>}
                    </div>
                  </div>
                  {isOpen && (
                    <div className="bg-slate-50 border-t border-slate-100">
                      {r.treatment && (
                        <div className="px-5 py-3 ml-0 border-b border-slate-100">
                          <p className="text-xs font-medium text-slate-600 mb-1">Treatment Plan</p>
                          <p className="text-sm text-slate-700">{r.treatment}</p>
                        </div>
                      )}
                      <div className="border-t border-slate-100">
                        <PrescriptionPanel recordId={r.record_id} />
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      <MedicalRecordModal open={modalOpen} onClose={() => setModalOpen(false)} record={editing} onSaved={() => { setModalOpen(false); load(); }} />
      <ConfirmDialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={handleDelete} loading={deleting}
        title="Delete Record" message="Delete this medical record?" />
    </div>
  );
}
