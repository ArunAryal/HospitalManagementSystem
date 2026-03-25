'use client';

import { useState, useEffect } from 'react';
import { Modal, Field, Spinner, ErrorBanner } from '@/components/ui';
import { patientsApi } from '@/lib/api';
import { parseValidationError } from '@/lib/utils';
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
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (patient) {
      const { patient_id, registration_date, ...rest } = patient as any;
      setForm(rest);
    } else {
      setForm(EMPTY);
    }
    setError('');
    setFieldErrors({});
  }, [patient, open]);

  const set = (k: keyof PatientCreate, v: any) => {
    setForm(f => ({ ...f, [k]: v }));
    setFieldErrors(e => ({ ...e, [k]: '' })); // Clear error when field is edited
  };

  const handleSubmit = async () => {
    const errors: Record<string, string> = {};
    if (!form.first_name) errors.first_name = 'Required';
    if (!form.last_name) errors.last_name = 'Required';
    if (!form.date_of_birth) errors.date_of_birth = 'Required';

    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      setError('Please fill in all required fields.');
      return;
    }

    setLoading(true);
    setError('');
    setFieldErrors({});
    try {
      if (patient) {
        await patientsApi.update(patient.patient_id, form);
      } else {
        await patientsApi.create(form);
      }
      onSaved();
    } catch (e: any) {
      const msg = e?.message || e?.toString?.() || 'An error occurred';
      const parsed = parseValidationError(msg);
      if (Object.keys(parsed).length > 0) {
        setFieldErrors(parsed);
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={patient ? 'Edit Patient' : 'Register Patient'} size="lg">
      {error && <div className="mb-4"><ErrorBanner message={error} /></div>}
      <div className="grid grid-cols-3 gap-4">
        <Field label="First Name" required error={fieldErrors.first_name}>
          <input className="input" value={form.first_name} onChange={e => set('first_name', e.target.value)} placeholder="John" />
        </Field>
        <Field label="Last Name" required error={fieldErrors.last_name}>
          <input className="input" value={form.last_name} onChange={e => set('last_name', e.target.value)} placeholder="Doe" />
        </Field>
        <Field label="Date of Birth" required error={fieldErrors.date_of_birth}>
          <input type="date" className="input" value={form.date_of_birth} onChange={e => set('date_of_birth', e.target.value)} />
        </Field>
        <Field label="Gender" required error={fieldErrors.gender}>
          <select className="input" value={form.gender} onChange={e => set('gender', e.target.value as Gender)}>
            {GENDERS.map(g => <option key={g}>{g}</option>)}
          </select>
        </Field>
        <Field label="Blood Group" error={fieldErrors.blood_group}>
          <select className="input" value={form.blood_group ?? ''} onChange={e => set('blood_group', e.target.value || undefined)}>
            <option value="">— Select —</option>
            {BLOOD_TYPES.map(b => <option key={b} value={b}>{b}</option>)}
          </select>
        </Field>
        <Field label="Phone" error={fieldErrors.phone}>
          <input className="input" value={form.phone ?? ''} onChange={e => set('phone', e.target.value || undefined)} placeholder="+977" />
        </Field>
        <Field label="Email" error={fieldErrors.email}>
          <input type="email" className="input" value={form.email ?? ''} onChange={e => set('email', e.target.value || undefined)} placeholder="patient@email.com" />
        </Field>
        <Field label="Address" error={fieldErrors.address}>
          <input className="input" value={form.address ?? ''} onChange={e => set('address', e.target.value || undefined)} placeholder="Street address" />
        </Field>
        <Field label="Emergency Contact" error={fieldErrors.emergency_contact}>
          <input className="input" value={form.emergency_contact ?? ''} onChange={e => set('emergency_contact', e.target.value || undefined)} placeholder="Name and phone" />
        </Field>
      </div>
      <div className="flex justify-end gap-3 mt-6">
        <button className="btn-secondary" onClick={onClose}>Cancel</button>
        <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading && <Spinner size="sm" />}
          {patient ? 'Save Changes' : 'Register Patient'}
        </button>
      </div>
    </Modal>
  );
}
