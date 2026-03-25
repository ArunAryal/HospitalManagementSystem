'use client';

import { useState, useEffect } from 'react';
import { Modal, Field, Spinner, ErrorBanner } from '@/components/ui';
import { appointmentsApi, patientsApi, doctorsApi } from '@/lib/api';
import { Appointment, AppointmentCreate, Patient, Doctor } from '@/types';

const EMPTY: AppointmentCreate = {
  patient_id: 0, doctor_id: 0,
  appointment_date: new Date().toISOString().split('T')[0],
  appointment_time: '09:00',
};

export default function AppointmentModal({ open, onClose, appointment, onSaved }: {
  open: boolean; onClose: () => void; appointment: Appointment | null; onSaved: () => void;
}) {
  const [form, setForm] = useState<AppointmentCreate>(EMPTY);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([patientsApi.list(0, 500), doctorsApi.list(0, 500)])
      .then(([p, d]) => { setPatients(p); setDoctors(d); });
  }, []);

  useEffect(() => {
    if (appointment) {
      setForm({
        patient_id: appointment.patient_id,
        doctor_id: appointment.doctor_id,
        appointment_date: appointment.appointment_date,
        appointment_time: appointment.appointment_time,
        reason: appointment.reason,
        notes: appointment.notes,
      });
    } else {
      setForm(EMPTY);
    }
    setError('');
  }, [appointment, open]);

  const set = (k: keyof AppointmentCreate, v: any) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async () => {
    if (!form.patient_id || !form.doctor_id || !form.appointment_date || !form.appointment_time) {
      setError('Patient, doctor, date, and time are required.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      if (appointment) {
        await appointmentsApi.update(appointment.appointment_id, form);
      } else {
        await appointmentsApi.create(form);
      }
      onSaved();
    } catch (e: any) {
      setError(e?.message || e?.toString?.() || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={appointment ? 'Edit Appointment' : 'Book Appointment'} size="lg">
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
            {doctors.map(d => <option key={d.doctor_id} value={d.doctor_id}>Dr. {d.first_name} {d.last_name} — {d.specialization}</option>)}
          </select>
        </Field>
        <Field label="Date" required>
          <input type="date" className="input" value={form.appointment_date} onChange={e => set('appointment_date', e.target.value)} />
        </Field>
        <Field label="Time" required>
          <input type="time" className="input" value={form.appointment_time} onChange={e => set('appointment_time', e.target.value)} />
        </Field>
        <div className="col-span-2">
          <Field label="Reason for Visit">
            <input className="input" value={form.reason ?? ''} onChange={e => set('reason', e.target.value || undefined)} placeholder="e.g. Regular checkup" />
          </Field>
        </div>
        <div className="col-span-3">
          <Field label="Notes">
            <textarea className="input min-h-[60px] resize-none" value={form.notes ?? ''} onChange={e => set('notes', e.target.value || undefined)} />
          </Field>
        </div>
      </div>
      <div className="flex justify-end gap-2 mt-4">
        <button className="btn-secondary" onClick={onClose}>Cancel</button>
        <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading && <Spinner size="sm" />}
          {appointment ? 'Save Changes' : 'Book Appointment'}
        </button>
      </div>
    </Modal>
  );
}
