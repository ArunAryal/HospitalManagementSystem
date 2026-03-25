'use client';

import { useEffect, useState } from 'react';
import { Plus, Pill, Pencil, Trash2, AlertTriangle } from 'lucide-react';
import { medicinesApi } from '@/lib/api';
import { Medicine, MedicineCreate } from '@/types';
import { formatCurrency } from '@/lib/utils';
import { PageLoader, EmptyState, ErrorBanner, SearchInput, ConfirmDialog, Modal, Field, Spinner } from '@/components/ui';

const EMPTY: MedicineCreate = { medicine_name: '', unit_price: 0, stock_quantity: 0 };

export default function MedicinesPage() {
  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Medicine | null>(null);
  const [form, setForm] = useState<MedicineCreate>(EMPTY);
  const [saving, setSaving] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Medicine | null>(null);

  const load = async () => {
    try { setMedicines(await medicinesApi.list(0, 500)); }
    catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  useEffect(() => {
    if (editing) {
      const { medicine_id, created_at, ...rest } = editing as any;
      setForm(rest);
    } else {
      setForm(EMPTY);
    }
  }, [editing, modalOpen]);

  const filtered = medicines.filter(m => {
    const q = search.toLowerCase();
    return m.medicine_name.toLowerCase().includes(q) || m.manufacturer?.toLowerCase().includes(q);
  });

  const handleSave = async () => {
    if (!form.medicine_name) return;
    setSaving(true);
    try {
      if (editing) {
        await medicinesApi.update(editing.medicine_id, form);
      } else {
        await medicinesApi.create(form);
      }
      setModalOpen(false);
      load();
    } catch (e: any) { setError(e.message); }
    finally { setSaving(false); }
  };

  const [deleting, setDeleting] = useState(false);
  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await medicinesApi.delete(deleteTarget.medicine_id);
      setDeleteTarget(null);
      load();
    } catch (e: any) { setError(e.message); }
    finally { setDeleting(false); }
  };

  if (loading) return <PageLoader />;

  const lowStock = medicines.filter(m => m.stock_quantity < 10).length;

  return (
    <div className="space-y-4 animate-fade-in-up">
      {error && <ErrorBanner message={error} />}
      {lowStock > 0 && (
        <div className="flex items-center gap-3 px-4 py-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-700">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          {lowStock} medicine{lowStock > 1 ? 's are' : ' is'} low on stock (less than 10 units)
        </div>
      )}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Medicines</h1>
          <p className="text-sm text-slate-500 mt-0.5">{medicines.length} items in inventory</p>
        </div>
        <button className="btn-primary" onClick={() => { setEditing(null); setModalOpen(true); }}>
          <Plus className="w-4 h-4" /> Add Medicine
        </button>
      </div>

      <div className="card px-4 py-3 flex items-center gap-3">
        <SearchInput value={search} onChange={setSearch} placeholder="Search by name or manufacturer…" />
        <span className="text-xs text-slate-400 ml-auto">{filtered.length} results</span>
      </div>

      <div className="card overflow-hidden">
        {filtered.length === 0 ? (
          <EmptyState icon={<Pill className="w-10 h-10" />} title="No medicines found"
            action={<button className="btn-primary" onClick={() => { setEditing(null); setModalOpen(true); }}><Plus className="w-4 h-4" /> Add Medicine</button>} />
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-100">
              <tr>{['Medicine', 'Manufacturer', 'Unit Price', 'Stock', ''].map(h =>
                <th key={h} className="table-header px-4 py-3 text-left">{h}</th>)}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {filtered.map(m => (
                <tr key={m.medicine_id} className="hover:bg-slate-50/60">
                  <td className="px-4 py-3">
                    <p className="font-medium text-slate-800">{m.medicine_name}</p>
                    {m.description && <p className="text-xs text-slate-400 mt-0.5 line-clamp-1">{m.description}</p>}
                  </td>
                  <td className="px-4 py-3 text-slate-500">{m.manufacturer ?? '—'}</td>
                  <td className="px-4 py-3 font-medium text-slate-700">{formatCurrency(m.unit_price)}</td>
                  <td className="px-4 py-3">
                    <span className={`badge ${m.stock_quantity < 10 ? 'bg-red-50 text-red-700 ring-red-200' : m.stock_quantity < 50 ? 'bg-amber-50 text-amber-700 ring-amber-200' : 'bg-emerald-50 text-emerald-700 ring-emerald-200'}`}>
                      {m.stock_quantity} units
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <button onClick={() => { setEditing(m); setModalOpen(true); }}
                        className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100">
                        <Pencil className="w-3.5 h-3.5" />
                      </button>
                      <button onClick={() => setDeleteTarget(m)}
                        className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-red-50 hover:text-red-600">
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit Medicine' : 'Add Medicine'} size="lg">
        <div className="grid grid-cols-3 gap-3">
          <Field label="Medicine Name" required>
            <input className="input" value={form.medicine_name} onChange={e => setForm(f => ({ ...f, medicine_name: e.target.value }))} />
          </Field>
          <Field label="Manufacturer">
            <input className="input" value={form.manufacturer ?? ''} onChange={e => setForm(f => ({ ...f, manufacturer: e.target.value || undefined }))} />
          </Field>
          <Field label="Description">
            <input className="input" value={form.description ?? ''} onChange={e => setForm(f => ({ ...f, description: e.target.value || undefined }))} placeholder="Brief description…" />
          </Field>
          <Field label="Unit Price ($)" required>
            <input type="number" step="0.01" min="0" className="input" value={form.unit_price || ''} onChange={e => setForm(f => ({ ...f, unit_price: e.target.value ? +e.target.value : 0 }))} />
          </Field>
          <Field label="Stock Quantity" required>
            <input type="number" min="0" className="input" value={form.stock_quantity || ''} onChange={e => setForm(f => ({ ...f, stock_quantity: e.target.value ? +e.target.value : 0 }))} />
          </Field>
        </div>
        <div className="flex justify-end gap-2 mt-4">
          <button className="btn-secondary" onClick={() => setModalOpen(false)}>Cancel</button>
          <button className="btn-primary" onClick={handleSave} disabled={saving}>
            {saving && <Spinner size="sm" />}{editing ? 'Save Changes' : 'Add Medicine'}
          </button>
        </div>
      </Modal>

      <ConfirmDialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete} loading={deleting}
        title="Delete Medicine" message={`Delete ${deleteTarget?.medicine_name}?`} />
    </div>
  );
}
