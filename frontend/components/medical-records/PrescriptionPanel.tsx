'use client';

import { useEffect, useState } from 'react';
import { Plus, Pill } from 'lucide-react';
import { medicalRecordsApi, medicinesApi } from '@/lib/api';
import { Prescription, Medicine } from '@/types';
import { Spinner, ErrorBanner, Modal, Field } from '@/components/ui';

export default function PrescriptionPanel({ recordId }: { recordId: number }) {
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [addOpen, setAddOpen] = useState(false);
  const [form, setForm] = useState({ medicine_id: 0, dosage: '', frequency: '', duration: '7 days', notes: '', quantity: 1 });
  const [saving, setSaving] = useState(false);

  const load = async () => {
    try {
      const [p, m] = await Promise.all([
        medicalRecordsApi.prescriptions(recordId),
        medicinesApi.list(0, 500),
      ]);
      setPrescriptions(p);
      setMedicines(m);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [recordId]);

  const handleAdd = async () => {
    if (!form.medicine_id || !form.dosage || !form.frequency || !form.quantity) {
      setError('Please fill all required fields (Medicine, Dosage, Frequency, Quantity)');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await medicalRecordsApi.addPrescription(recordId, { 
        ...form, 
        medical_record_id: recordId 
      });
      setAddOpen(false);
      setForm({ medicine_id: 0, dosage: '', frequency: '', duration: '7 days', notes: '', quantity: 1 });
      await load();
    } catch (e: any) {
      setError(e?.message || 'Failed to add prescription');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="flex justify-center py-4"><Spinner /></div>;

  return (
    <div className="px-5 py-4">
      {error && <div className="mb-3"><ErrorBanner message={error} /></div>}
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Prescriptions</p>
        <button className="btn-secondary text-xs py-1" onClick={() => setAddOpen(true)}>
          <Plus className="w-3 h-3" /> Add
        </button>
      </div>
      {prescriptions.length === 0 ? (
        <p className="text-xs text-slate-400 py-2">No prescriptions for this record.</p>
      ) : (
        <div className="space-y-2">
          {prescriptions.map((p: any) => (
            <div key={p.prescription_id} className="flex items-center gap-3 bg-white border border-slate-100 rounded-lg px-3 py-2.5">
              <Pill className="w-4 h-4 text-brand-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-slate-800">{p.medicine?.medicine_name ?? `Medicine #${p.medicine_id}`}</p>
                <p className="text-xs text-slate-500">{p.dosage} · {p.frequency} · {p.duration}</p>
              </div>
              {p.notes && <p className="text-xs text-slate-400 truncate max-w-[120px]">{p.notes}</p>}
            </div>
          ))}
        </div>
      )}

      <Modal open={addOpen} onClose={() => setAddOpen(false)} title="Add Prescription" size="lg">
        {error && <div className="mb-3"><ErrorBanner message={error} /></div>}
        <div className="space-y-3">
          <Field label="Medicine" required>
            <select className="input" value={form.medicine_id} onChange={e => setForm(f => ({ ...f, medicine_id: +e.target.value }))}>
              <option value={0}>— Select medicine —</option>
              {medicines.map(m => <option key={m.medicine_id} value={m.medicine_id}>{m.medicine_name}</option>)}
            </select>
          </Field>
          <Field label="Dosage" required>
            <input className="input" value={form.dosage} placeholder="e.g. 500mg" onChange={e => setForm(f => ({ ...f, dosage: e.target.value }))} />
          </Field>
          <Field label="Frequency" required>
            <input className="input" value={form.frequency} placeholder="e.g. Twice daily" onChange={e => setForm(f => ({ ...f, frequency: e.target.value }))} />
          </Field>
          <Field label="Quantity" required>
            <input type="number" min="1" className="input" value={form.quantity || ''} onChange={e => setForm(f => ({ ...f, quantity: e.target.value ? +e.target.value : 0 }))} placeholder="e.g. 1" />
          </Field>
          <Field label="Duration" required>
            <input className="input" value={form.duration} placeholder="e.g. 7 days" onChange={e => setForm(f => ({ ...f, duration: e.target.value }))} />
          </Field>
          <Field label="Notes">
            <input className="input" value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} />
          </Field>
        </div>
        <div className="flex justify-end gap-2 mt-4">
          <button className="btn-secondary" onClick={() => setAddOpen(false)}>Cancel</button>
          <button className="btn-primary" onClick={handleAdd} disabled={saving}>
            {saving && <Spinner size="sm" />} Add Prescription
          </button>
        </div>
      </Modal>
    </div>
  );
}
