'use client';

import { useState, useEffect } from 'react';
import { Modal, Field, Spinner, ErrorBanner } from '@/components/ui';
import { patientsApi, doctorsApi, billingApi } from '@/lib/api';
import { AdmissionCreate, Patient, Doctor, Room } from '@/types';

interface AdmitPatientModalProps {
  open: boolean;
  onClose: () => void;
  onSaved: () => void;
  initialRoomId?: number;
}

export default function AdmitPatientModal({ open, onClose, onSaved, initialRoomId }: AdmitPatientModalProps) {
  const [form, setForm] = useState<AdmissionCreate>({
    patient_id: 0,
    room_id: initialRoomId || 0,
    doctor_id: 0,
    admission_date: new Date().toISOString().split('T')[0],
    reason: ''
  });
  
  const [patients, setPatients] = useState<Patient[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loadingItems, setLoadingItems] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (open) {
      setForm(f => ({ ...f, room_id: initialRoomId || 0 }));
      loadData();
    }
  }, [open, initialRoomId]);

  const loadData = async () => {
    setLoadingItems(true);
    try {
      const [p, d, r] = await Promise.all([
        patientsApi.list(0, 500),
        doctorsApi.list(0, 500),
        billingApi.listRooms(0, 500)
      ]);
      setPatients(p);
      setDoctors(d);
      setRooms(r);
    } catch (e: any) {
      setError('Failed to load required data');
    } finally {
      setLoadingItems(false);
    }
  };

  const handleSave = async () => {
    if (!form.patient_id || !form.room_id || !form.doctor_id || !form.reason) {
      setError('Please fill all required fields');
      return;
    }
    
    setSaving(true);
    setError('');
    try {
      await billingApi.createAdmission(form);
      setForm({
        patient_id: 0,
        room_id: 0,
        doctor_id: 0,
        admission_date: new Date().toISOString().split('T')[0],
        reason: ''
      });
      onSaved();
      onClose();
    } catch (e: any) {
      setError(e?.message || e?.toString?.() || 'An error occurred');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="Admit Patient" size="lg">
      {error && <div className="mb-3"><ErrorBanner message={error} /></div>}
      
      {loadingItems && !patients.length ? (
        <div className="py-8 flex justify-center"><Spinner /></div>
      ) : (
        <>
          <div className="grid grid-cols-3 gap-3">
            <Field label="Patient" required>
              <select className="input" value={form.patient_id} onChange={e => setForm(f => ({ ...f, patient_id: +e.target.value }))}>
                <option value={0}>— Select patient —</option>
                {patients.map(p => <option key={p.patient_id} value={p.patient_id}>{p.first_name} {p.last_name}</option>)}
              </select>
            </Field>
            
            <Field label="Room" required>
              <select className="input" value={form.room_id} onChange={e => setForm(f => ({ ...f, room_id: +e.target.value }))}>
                <option value={0}>— Select room —</option>
                {rooms.filter(r => r.is_available || r.room_id === initialRoomId).map(r => 
                  <option key={r.room_id} value={r.room_id}>Room {r.room_number} ({r.room_type})</option>
                )}
              </select>
            </Field>
            
            <Field label="Doctor" required>
              <select className="input" value={form.doctor_id} onChange={e => setForm(f => ({ ...f, doctor_id: +e.target.value }))}>
                <option value={0}>— Select doctor —</option>
                {doctors.map(d => <option key={d.doctor_id} value={d.doctor_id}>Dr. {d.first_name} {d.last_name}</option>)}
              </select>
            </Field>
            
            <Field label="Admission Date" required>
              <input type="date" className="input" value={form.admission_date} onChange={e => setForm(f => ({ ...f, admission_date: e.target.value }))} />
            </Field>
            
            <div className="col-span-2">
              <Field label="Reason" required>
                <input className="input" value={form.reason} onChange={e => setForm(f => ({ ...f, reason: e.target.value }))} placeholder="e.g. Broken Arm" />
              </Field>
            </div>
          </div>
          
          <div className="flex justify-end gap-2 mt-4">
            <button className="btn-secondary" onClick={onClose}>Cancel</button>
            <button className="btn-primary" onClick={handleSave} disabled={saving}>
              {saving && <Spinner size="sm" />} Admit Patient
            </button>
          </div>
        </>
      )}
    </Modal>
  );
}
