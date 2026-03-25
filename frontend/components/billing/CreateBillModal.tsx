'use client';

import { useState, useEffect } from 'react';
import { Modal, Field, Spinner, ErrorBanner } from '@/components/ui';
import { billingApi, patientsApi } from '@/lib/api';
import { BillCreate, Patient } from '@/types';

interface CreateBillModalProps {
  open: boolean;
  onClose: () => void;
  onSaved: () => void;
}

export default function CreateBillModal({ open, onClose, onSaved }: CreateBillModalProps) {
  const [form, setForm] = useState<BillCreate>({ patient_id: 0, total_amount: 0 });
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loadingItems, setLoadingItems] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (open) loadData();
  }, [open]);

  const loadData = async () => {
    setLoadingItems(true);
    try {
      setPatients(await patientsApi.list(0, 500));
    } catch (e: any) {
      setError('Failed to load patients');
    } finally {
      setLoadingItems(false);
    }
  };

  const handleSave = async () => {
    if (!form.patient_id || !form.total_amount) {
      setError('Please fill all required fields');
      return;
    }
    
    setSaving(true);
    setError('');
    try {
      await billingApi.createBill(form);
      setForm({ patient_id: 0, total_amount: 0 });
      onSaved();
    } catch (e: any) {
      setError(e?.message || e?.toString?.() || 'An error occurred');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="Create Bill" size="lg">
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
            
            <Field label="Total Amount ($)" required>
              <input type="number" min="0" step="0.01" className="input" value={form.total_amount}
                onChange={e => setForm(f => ({ ...f, total_amount: +e.target.value }))} />
            </Field>
            
            <Field label="Bill Date">
              <input type="date" className="input" value={form.bill_date ?? ''} onChange={e => setForm((f: any) => ({ ...f, bill_date: e.target.value || undefined }))} />
            </Field>
          </div>
          
          <div className="flex justify-end gap-2 mt-4">
            <button className="btn-secondary" onClick={onClose}>Cancel</button>
            <button className="btn-primary" onClick={handleSave} disabled={saving}>
              {saving && <Spinner size="sm" />} Create Bill
            </button>
          </div>
        </>
      )}
    </Modal>
  );
}
