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
  const [patientSearch, setPatientSearch] = useState('');
  const [patients, setPatients] = useState<Patient[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPatientResults, setShowPatientResults] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  // Load all doctors on mount
  useEffect(() => {
    doctorsApi.list(0, 500).then(setDoctors);
  }, []);

  // Search patients as user types
  useEffect(() => {
    // If a patient is already selected, don't show search results
    if (selectedPatient) {
      setShowPatientResults(false);
      return;
    }

    if (patientSearch.length >= 2) {
      setSearchLoading(true);
      patientsApi.search(patientSearch, 0, 10)
        .then(results => {
          setPatients(results);
          setShowPatientResults(true);
        })
        .catch(err => {
          console.error('Search error:', err);
          setPatients([]);
        })
        .finally(() => setSearchLoading(false));
    } else {
      setPatients([]);
      setShowPatientResults(false);
    }
  }, [patientSearch, selectedPatient]);

  useEffect(() => {
    if (record) {
      setForm({ patient_id: record.patient_id, doctor_id: record.doctor_id, record_date: record.record_date, diagnosis: record.diagnosis, treatment: record.treatment, notes: record.notes });
      setSelectedPatient(null);
      setPatientSearch('');
    } else {
      setForm(EMPTY);
      setSelectedPatient(null);
      setPatientSearch('');
    }
    setError('');
  }, [record, open]);

  const set = (k: keyof MedicalRecordCreate, v: any) => setForm(f => ({ ...f, [k]: v }));

  const handleSelectPatient = async (patient: Patient) => {
    setSelectedPatient(patient);
    setForm(f => ({ ...f, patient_id: patient.patient_id }));
    setPatientSearch(`${patient.first_name} ${patient.last_name}`);
    setShowPatientResults(false);

    // Fetch patient's recent doctor
    try {
      const result = await patientsApi.getWithDoctor(patient.patient_id);
      if (result.doctor) {
        setForm(f => ({ ...f, doctor_id: result.doctor.doctor_id }));
      }
    } catch (err) {
      console.error('Error fetching patient doctor:', err);
    }
  };

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
          <div className="relative">
            <input 
              type="text"
              className="input"
              placeholder="Search patient by name..."
              value={patientSearch}
              onChange={e => {
                const newValue = e.target.value;
                setPatientSearch(newValue);
                // Clear selection if user starts typing something different
                if (selectedPatient && newValue !== `${selectedPatient.first_name} ${selectedPatient.last_name}`) {
                  setSelectedPatient(null);
                }
              }}
              onFocus={() => {
                // Only show results if we have a search and no selection
                if (patientSearch.length >= 2 && !selectedPatient) {
                  setShowPatientResults(true);
                }
              }}
            />
            {showPatientResults && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded shadow-lg z-10 max-h-48 overflow-y-auto">
                {searchLoading && <div className="p-2 text-sm text-gray-600">Searching...</div>}
                {!searchLoading && patients.length === 0 && patientSearch.length >= 2 && (
                  <div className="p-2 text-sm text-gray-600">No patients found</div>
                )}
                {patients.map(p => (
                  <div
                    key={p.patient_id}
                    className="p-2 hover:bg-blue-100 cursor-pointer text-sm border-b last:border-b-0"
                    onClick={() => handleSelectPatient(p)}
                  >
                    {p.first_name} {p.last_name} {p.phone && `(${p.phone})`}
                  </div>
                ))}
              </div>
            )}
            {selectedPatient && !showPatientResults && (
              <div className="text-sm text-gray-600 mt-1">
                Selected: {selectedPatient.first_name} {selectedPatient.last_name}
              </div>
            )}
          </div>
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
