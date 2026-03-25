'use client';

import { useState, useEffect } from 'react';
import { Modal, Field, Spinner, ErrorBanner } from '@/components/ui';
import { doctorsApi } from '@/lib/api';
import { parseValidationError } from '@/lib/utils';
import { Doctor, DoctorCreate } from '@/types';

const EMPTY: DoctorCreate = {
  first_name: '', last_name: '', specialization: '', phone: '', email: '', consultation_fee: 0, joined_date: new Date().toISOString().split('T')[0], is_available: true,
};

export default function DoctorModal({ open, onClose, doctor, onSaved }: {
  open: boolean; onClose: () => void; doctor: Doctor | null; onSaved: () => void;
}) {
  const [form, setForm] = useState<DoctorCreate>(EMPTY);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (doctor) {
      const { doctor_id, ...rest } = doctor as any;
      setForm(rest);
    } else {
      setForm(EMPTY);
    }
    setError('');
    setFieldErrors({});
  }, [doctor, open]);

  const set = (k: keyof DoctorCreate, v: any) => {
    setForm(f => ({ ...f, [k]: v }));
    setFieldErrors(e => ({ ...e, [k]: '' })); // Clear error when field is edited
  };

  const handleSubmit = async () => {
    const errors: Record<string, string> = {};
    if (!form.first_name) errors.first_name = 'Required';
    if (!form.last_name) errors.last_name = 'Required';
    if (!form.specialization) errors.specialization = 'Required';
    if (!form.consultation_fee) errors.consultation_fee = 'Required';
    if (!form.email) errors.email = 'Required';
    
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      setError('Please fill in all required fields.');
      return;
    }

    setLoading(true);
    setError('');
    setFieldErrors({});
    try {
      if (doctor) {
        await doctorsApi.update(doctor.doctor_id, form);
      } else {
        await doctorsApi.create(form);
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
    <Modal open={open} onClose={onClose} title={doctor ? 'Edit Doctor' : 'Add Doctor'} size="lg">
      {error && <div className="mb-4"><ErrorBanner message={error} /></div>}
      <div className="grid grid-cols-3 gap-4">
        <Field label="First Name" required error={fieldErrors.first_name}>
          <input className="input" value={form.first_name} onChange={e => set('first_name', e.target.value)} placeholder="John" />
        </Field>
        <Field label="Last Name" required error={fieldErrors.last_name}>
          <input className="input" value={form.last_name} onChange={e => set('last_name', e.target.value)} placeholder="Doe" />
        </Field>
        <Field label="Specialization" required error={fieldErrors.specialization}>
          <input className="input" value={form.specialization} onChange={e => set('specialization', e.target.value)} placeholder="e.g. Cardiology" />
        </Field>
        <Field label="Qualification" error={fieldErrors.qualification}>
          <input className="input" value={form.qualification ?? ''} onChange={e => set('qualification', e.target.value || undefined)} placeholder="MBBS, MD" />
        </Field>
        <Field label="Consultation Fee (Rs)" required error={fieldErrors.consultation_fee}>
          <input type="number" min="0" step="0.01" className="input" value={form.consultation_fee || ''} onChange={e => set('consultation_fee', e.target.value ? +e.target.value : 0)} />
        </Field>
        <Field label="Experience (Years)" error={fieldErrors.experience_years}>
          <input type="number" min="0" className="input" value={form.experience_years ?? ''} onChange={e => set('experience_years', e.target.value ? +e.target.value : undefined)} />
        </Field>
        <Field label="Joined Date" required error={fieldErrors.joined_date}>
          <input type="date" className="input" value={form.joined_date} onChange={e => set('joined_date', e.target.value)} />
        </Field>
        <Field label="Phone" error={fieldErrors.phone}>
          <input className="input" value={form.phone ?? ''} onChange={e => set('phone', e.target.value || undefined)} placeholder="+977-9841234567" />
        </Field>
        <Field label="Email" required error={fieldErrors.email}>
          <input type="email" className="input" value={form.email ?? ''} onChange={e => set('email', e.target.value || undefined)} placeholder="doctor@hospital.com" />
        </Field>
        <div className="col-span-3 flex items-center gap-3 px-4 py-3 bg-slate-50 rounded-lg border border-slate-100">
          <input
            type="checkbox" id="available" checked={form.is_available ?? true}
            onChange={e => set('is_available', e.target.checked)}
            className="w-4 h-4 accent-brand-600 cursor-pointer rounded"
          />
          <label htmlFor="available" className="text-sm text-slate-700 cursor-pointer font-medium">Currently available for appointments</label>
        </div>
      </div>
      <div className="flex justify-end gap-3 mt-6">
        <button className="btn-secondary" onClick={onClose}>Cancel</button>
        <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading && <Spinner size="sm" />}
          {doctor ? 'Save Changes' : 'Add Doctor'}
        </button>
      </div>
    </Modal>
  );
}
