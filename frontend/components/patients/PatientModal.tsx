'use client';

import { useState, useEffect } from 'react';
import { Modal, Field, Spinner, ErrorBanner } from '@/components/ui';
import { patientsApi } from '@/lib/api';
import { Patient, PatientCreate, Gender, BloodType } from '@/types';

const GENDERS: Gender[] = ['Male', 'Female', 'Other'];
const BLOOD_TYPES: BloodType[] = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

const EMPTY: PatientCreate = {
  first_name: '', last_name: '', date_of_birth: '', gender: 'Male', phone: '',
};

export default function PatientModal({ open, onClose, patient, onSaved }: {
  open: boolean;
  onClose: () => void;
  patient: Patient | null;
  onSaved: () => void;
}) {
  const [form, setForm] = useState<PatientCreate>(EMPTY);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (patient) {
      const { patient_id, registration_date, ...rest } = patient as any;
      setForm(rest);
    } else {
      setForm(EMPTY);
    }
    setError('');
  }, [patient, open]);

  const set = (k: keyof PatientCreate, v: any) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async () => {
    if (!form.first_name || !form.last_name || !form.date_of_birth) {
      setError('First name, last name, and date of birth are required.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      if (patient) {
        await patientsApi.update(patient.patient_id, form);
      } else {
        await patientsApi.create(form);
      }
      onSaved();
    } catch (e: any) {
      setError(e?.message || e?.toString?.() || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={patient ? 'Edit Patient' : 'Register Patient'} size="lg">
      {error && <div className="mb-3"><ErrorBanner message={error} /></div>}
      <div className="grid grid-cols-3 gap-3">
        <Field label="First Name" required>
          <input className="input" value={form.first_name} onChange={e => set('first_name', e.target.value)} />
        </Field>
        <Field label="Last Name" required>
          <input className="input" value={form.last_name} onChange={e => set('last_name', e.target.value)} />
        </Field>
        <Field label="Date of Birth" required>
          <input type="date" className="input" value={form.date_of_birth} onChange={e => set('date_of_birth', e.target.value)} />
        </Field>
        <Field label="Gender" required>
          <select className="input" value={form.gender} onChange={e => set('gender', e.target.value as Gender)}>
            {GENDERS.map(g => <option key={g}>{g}</option>)}
          </select>
        </Field>
        <Field label="Blood Group">
          <select className="input" value={form.blood_group ?? ''} onChange={e => set('blood_group', e.target.value || undefined)}>
            <option value="">— Select —</option>
            {BLOOD_TYPES.map(b => <option key={b} value={b}>{b}</option>)}
          </select>
        </Field>
        <Field label="Phone">
          <input className="input" value={form.phone ?? ''} onChange={e => set('phone', e.target.value || undefined)} />
        </Field>
        <Field label="Email">
          <input type="email" className="input" value={form.email ?? ''} onChange={e => set('email', e.target.value || undefined)} />
        </Field>
        <Field label="Address">
          <input className="input" value={form.address ?? ''} onChange={e => set('address', e.target.value || undefined)} />
        </Field>
        <Field label="Emergency Contact">
          <input className="input" value={form.emergency_contact ?? ''} onChange={e => set('emergency_contact', e.target.value || undefined)} placeholder="Name and/or Phone" />
        </Field>
      </div>
      <div className="flex justify-end gap-2 mt-4">
        <button className="btn-secondary" onClick={onClose}>Cancel</button>
        <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading && <Spinner size="sm" />}
          {patient ? 'Save Changes' : 'Register Patient'}
        </button>
      </div>
    </Modal>
  );
}
