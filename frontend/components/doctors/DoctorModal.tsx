'use client';

import { useState, useEffect } from 'react';
import { Modal, Field, Spinner, ErrorBanner } from '@/components/ui';
import { doctorsApi } from '@/lib/api';
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

  useEffect(() => {
    if (doctor) {
      const { doctor_id, ...rest } = doctor as any;
      setForm(rest);
    } else {
      setForm(EMPTY);
    }
    setError('');
  }, [doctor, open]);

  const set = (k: keyof DoctorCreate, v: any) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async () => {
    if (!form.first_name || !form.last_name || !form.specialization || !form.consultation_fee) {
      setError('First name, last name, specialization and fee are required.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      if (doctor) {
        await doctorsApi.update(doctor.doctor_id, form);
      } else {
        await doctorsApi.create(form);
      }
      onSaved();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={doctor ? 'Edit Doctor' : 'Add Doctor'} size="lg">
      {error && <div className="mb-3"><ErrorBanner message={error} /></div>}
      <div className="grid grid-cols-3 gap-3">
        <Field label="First Name" required>
          <input className="input" value={form.first_name} onChange={e => set('first_name', e.target.value)} />
        </Field>
        <Field label="Last Name" required>
          <input className="input" value={form.last_name} onChange={e => set('last_name', e.target.value)} />
        </Field>
        <Field label="Specialization" required>
          <input className="input" value={form.specialization} onChange={e => set('specialization', e.target.value)} placeholder="e.g. Cardiology" />
        </Field>
        <Field label="Qualification">
          <input className="input" value={form.qualification ?? ''} onChange={e => set('qualification', e.target.value || undefined)} />
        </Field>
        <Field label="Consultation Fee ($)" required>
          <input type="number" min="0" step="0.01" className="input" value={form.consultation_fee} onChange={e => set('consultation_fee', +e.target.value)} />
        </Field>
        <Field label="Experience (Years)">
          <input type="number" min="0" className="input" value={form.experience_years ?? ''} onChange={e => set('experience_years', e.target.value ? +e.target.value : undefined)} />
        </Field>
        <Field label="Joined Date" required>
          <input type="date" className="input" value={form.joined_date} onChange={e => set('joined_date', e.target.value)} />
        </Field>
        <Field label="Phone">
          <input className="input" value={form.phone ?? ''} onChange={e => set('phone', e.target.value || undefined)} />
        </Field>
        <Field label="Email">
          <input type="email" className="input" value={form.email ?? ''} onChange={e => set('email', e.target.value || undefined)} />
        </Field>
        <div className="col-span-3 flex items-center gap-2.5">
          <input
            type="checkbox" id="available" checked={form.is_available ?? true}
            onChange={e => set('is_available', e.target.checked)}
            className="w-4 h-4 accent-brand-600 cursor-pointer"
          />
          <label htmlFor="available" className="text-sm text-slate-700 cursor-pointer">Currently available for appointments</label>
        </div>
      </div>
      <div className="flex justify-end gap-2 mt-4">
        <button className="btn-secondary" onClick={onClose}>Cancel</button>
        <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading && <Spinner size="sm" />}
          {doctor ? 'Save Changes' : 'Add Doctor'}
        </button>
      </div>
    </Modal>
  );
}
