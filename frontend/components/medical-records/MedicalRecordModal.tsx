'use client';

import { useState, useEffect } from 'react';
import { Modal, Field, Spinner, ErrorBanner } from '@/components/ui';
import { medicalRecordsApi, patientsApi, doctorsApi } from '@/lib/api';
import { MedicalRecord, MedicalRecordCreate, Patient, Doctor } from '@/types';

const EMPTY: MedicalRecordCreate = {
  patient_id: 0, doctor_id: 0,
  record_date: new Date().toISOString().split('T')[0],
  diagnosis: '',
};

export default function MedicalRecordModal({ open, onClose, record, onSaved }: {
  open: boolean; onClose: () => void; record: MedicalRecord | null; onSaved: () => void;
}) {
  const [form, setForm] = useState<MedicalRecordCreate>(EMPTY);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([patientsApi.list(0, 500), doctorsApi.list(0, 500)])
      .then(([p, d]) => { setPatients(p); setDoctors(d); });
  }, []);

  useEffect(() => {
    if (record) {
      setForm({ patient_id: record.patient_id, doctor_id: record.doctor_id, record_date: record.record_date, diagnosis: record.diagnosis, treatment: record.treatment, notes: record.notes });
    } else {
      setForm(EMPTY);
    }
    setError('');
  }, [record, open]);

  const set = (k: keyof MedicalRecordCreate, v: any) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async () => {
    if (!form.patient_id || !form.doctor_id || !form.diagnosis) {
      setError('Patient, doctor, and diagnosis are required.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      if (record) {
        await medicalRecordsApi.update(record.record_id, form);
      } else {
        await medicalRecordsApi.create(form);
      }
      onSaved();
    } catch (e: any) {
      setError(e?.message || e?.toString?.() || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={record ? 'Edit Medical Record' : 'New Medical Record'} size="lg">
      {error && <div className="mb-3"><ErrorBanner message={error} /></div>}
      <div className="grid grid-cols-3 gap-3">
        <Field label="Patient" required>
          <select className="input" value={form.patient_id} onChange={e => set('patient_id', +e.target.value)}>
            <option value={0}>— Select patient —</option>
            {patients.map(p => <option key={p.patient_id} value={p.patient_id}>{p.first_name} {p.last_name}</option>)}
          </select>
        </Field>
        <Field label="Doctor" required>
          <select className="input" value={form.doctor_id} onChange={e => set('doctor_id', +e.target.value)}>
            <option value={0}>— Select doctor —</option>
            {doctors.map(d => <option key={d.doctor_id} value={d.doctor_id}>Dr. {d.first_name} {d.last_name}</option>)}
          </select>
        </Field>
        <Field label="Record Date" required>
          <input type="date" className="input" value={form.record_date} onChange={e => set('record_date', e.target.value)} />
        </Field>
        <Field label="Diagnosis" required>
          <input className="input" value={form.diagnosis} onChange={e => set('diagnosis', e.target.value)} placeholder="e.g. Hypertension" />
        </Field>
        <Field label="Treatment">
          <input className="input" value={form.treatment ?? ''} onChange={e => set('treatment', e.target.value || undefined)} placeholder="Treatment plan…" />
        </Field>
        <Field label="Notes">
          <input className="input" value={form.notes ?? ''} onChange={e => set('notes', e.target.value || undefined)} placeholder="Additional notes…" />
        </Field>
      </div>
      <div className="flex justify-end gap-2 mt-4">
        <button className="btn-secondary" onClick={onClose}>Cancel</button>
        <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading && <Spinner size="sm" />}
          {record ? 'Save Changes' : 'Create Record'}
        </button>
      </div>
    </Modal>
  );
}
