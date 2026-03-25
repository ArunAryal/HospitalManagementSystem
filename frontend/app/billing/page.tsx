'use client';

import { useEffect, useState } from 'react';
import { Receipt, CreditCard, RefreshCw } from 'lucide-react';
import { billingApi, patientsApi } from '@/lib/api';
import { Bill, BillStatus, PaymentCreate, PaymentMethod, Patient } from '@/types';
import { formatDate, formatCurrency } from '@/lib/utils';
import { PageLoader, ErrorBanner, StatusBadge, SearchInput, Modal, Field, Spinner, StatCard } from '@/components/ui';

const STATUSES: BillStatus[] = ['Pending', 'Paid', 'Partially Paid', 'Cancelled'];
const PAY_METHODS: PaymentMethod[] = ['Cash', 'Card', 'Insurance', 'Online'];

export default function BillingPage() {
  const [bills, setBills] = useState<Bill[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [payModal, setPayModal] = useState<Bill | null>(null);
  const [payForm, setPayForm] = useState<Omit<PaymentCreate, 'bill_id'>>({ amount: 0, payment_method: 'Cash' });
  const [saving, setSaving] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const load = async () => {
    try {
      const [b, p] = await Promise.all([billingApi.listBills(0, 500), patientsApi.list(0, 500)]);
      setBills(b); setPatients(p);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const filtered = bills.filter(b => {
    const q = search.toLowerCase();
    const p = (b as any).patient;
    const matchSearch = !q || (p ? `${p.first_name} ${p.last_name}`.toLowerCase().includes(q) : `${b.patient_id}`.includes(q));
    const matchStatus = !statusFilter || b.payment_status === statusFilter;
    return matchSearch && matchStatus;
  });

  const addPayment = async () => {
    if (!payModal || !payForm.amount) {
      setError('Please enter a payment amount');
      return;
    }
    setSaving(true);
    setError('');
    try {
      const newPaidAmount = Number((Number(payModal.paid_amount || 0) + Number(payForm.amount || 0)).toFixed(2));
      await billingApi.updateBill(payModal.bill_id, { 
        paid_amount: newPaidAmount, 
        payment_method: payForm.payment_method 
      });
      setPayModal(null);
      setPayForm({ amount: 0, payment_method: 'Cash' });
      await load();
    } catch (e: any) { 
      setError(e.message || 'Failed to record payment');
    } finally { 
      setSaving(false); 
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await load();
    } catch (e: any) { setError(e.message); }
    finally { setRefreshing(false); }
  };

  if (loading) return <PageLoader />;

  const totalPending = bills.filter(b => b.payment_status === 'Pending').reduce((s, b) => s + b.total_amount, 0);
  const totalCollected = bills.reduce((s, b) => s + b.paid_amount, 0);
  const totalOutstanding = bills.reduce((s, b) => s + (b.total_amount - b.paid_amount), 0);

  return (
    <div className="space-y-4 animate-fade-in-up">
      {error && <ErrorBanner message={error} />}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Billing</h1>
          <p className="text-sm text-slate-500 mt-0.5">{bills.length} bills total • Auto-generated from admissions and prescriptions</p>
        </div>
        <button 
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 font-medium text-sm transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard label="Total Collected" value={formatCurrency(totalCollected)} icon={<CreditCard className="w-5 h-5" />} color="green" />
        <StatCard label="Outstanding" value={formatCurrency(totalOutstanding)} icon={<Receipt className="w-5 h-5" />} color="red" />
        <StatCard label="Pending Bills" value={formatCurrency(totalPending)} icon={<Receipt className="w-5 h-5" />} color="amber" />
      </div>

      {/* Filters */}
      <div className="card px-4 py-3 flex items-center gap-3 flex-wrap">
        <SearchInput value={search} onChange={setSearch} placeholder="Search by patient name…" />
        <div className="flex gap-1.5">
          <button className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${!statusFilter ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
            onClick={() => setStatusFilter('')}>All</button>
          {STATUSES.map(s => (
            <button key={s} className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${statusFilter === s ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
              onClick={() => setStatusFilter(s === statusFilter ? '' : s)}>{s}</button>
          ))}
        </div>
        <span className="text-xs text-slate-400 ml-auto">{filtered.length} results</span>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-100">
            <tr>{['Patient', 'Total', 'Paid', 'Balance', 'Due Date', 'Status', ''].map(h =>
              <th key={h} className="table-header px-4 py-3 text-left">{h}</th>)}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {filtered.map(b => {
              const patient = (b as any).patient;
              const balance = b.total_amount - b.paid_amount;
              return (
                <tr key={b.bill_id} className="hover:bg-slate-50/60">
                  <td className="px-4 py-3 font-medium">
                    {patient ? `${patient.first_name} ${patient.last_name}` : `Patient #${b.patient_id}`}
                    <p className="text-xs text-slate-400 font-normal">Bill #{b.bill_id}</p>
                  </td>
                  <td className="px-4 py-3 font-semibold text-slate-800">{formatCurrency(b.total_amount)}</td>
                  <td className="px-4 py-3 text-emerald-600 font-medium">{formatCurrency(b.paid_amount)}</td>
                  <td className="px-4 py-3">
                    <span className={balance > 0 ? 'text-red-500 font-medium' : 'text-slate-400'}>{formatCurrency(balance)}</span>
                  </td>
                  <td className="px-4 py-3 text-slate-500 text-xs">{formatDate(b.bill_date)}</td>
                  <td className="px-4 py-3"><StatusBadge status={b.payment_status} /></td>
                  <td className="px-4 py-3">
                    {b.payment_status !== 'Paid' && b.payment_status !== 'Cancelled' && (
                      <button className="flex items-center gap-1 text-xs text-brand-600 hover:text-brand-700 font-medium px-2 py-1 rounded-lg hover:bg-brand-50"
                        onClick={() => { setPayForm({ amount: balance, payment_method: 'Cash' }); setPayModal(b); }}>
                        <CreditCard className="w-3 h-3" /> Pay
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="text-center py-12 text-sm text-slate-400">No bills found</div>
        )}
      </div>

      {/* Create Bill Modal */}
      {/* Removed: Bills are now auto-generated when admissions are created and prescriptions are added */}

      {/* Payment Modal */}
      <Modal open={!!payModal} onClose={() => setPayModal(null)} title="Record Payment" size="md">
        {payModal && (
          <>
            {error && <div className="mb-4"><ErrorBanner message={error} /></div>}
            <div className="bg-slate-50 rounded-lg p-3 mb-4 text-sm">
              <p className="text-slate-500">Outstanding balance</p>
              <p className="text-xl font-bold text-slate-900 mt-0.5">{formatCurrency(payModal.total_amount - payModal.paid_amount)}</p>
            </div>
            <div className="space-y-3">
              <Field label="Amount (Rs)" required>
                <input type="number" min="0" step="0.01" className="input" value={payForm.amount || ''}
                  onChange={e => setPayForm(f => ({ ...f, amount: e.target.value ? +e.target.value : 0 }))} />
              </Field>
              <Field label="Payment Method">
                <select className="input" value={payForm.payment_method} onChange={e => setPayForm(f => ({ ...f, payment_method: e.target.value as PaymentMethod }))}>
                  {PAY_METHODS.map(m => <option key={m}>{m}</option>)}
                </select>
              </Field>
            </div>
            <div className="flex justify-end gap-2 mt-5">
              <button className="btn-secondary" onClick={() => setPayModal(null)} disabled={saving}>Cancel</button>
              <button className="btn-primary" onClick={addPayment} disabled={saving}>{saving && <Spinner size="sm" />}Record Payment</button>
            </div>
          </>
        )}
      </Modal>
    </div>
  );
}
