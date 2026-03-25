'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Pencil, CalendarDays, FileText, Receipt } from 'lucide-react';
import { patientsApi } from '@/lib/api';
import { Patient, Appointment, MedicalRecord, Bill } from '@/types';
import { formatDate, calcAge, formatCurrency } from '@/lib/utils';
import { PageLoader, ErrorBanner, StatusBadge } from '@/components/ui';
import PatientModal from '@/components/patients/PatientModal';

function Section({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="card overflow-hidden">
      <div className="flex items-center gap-2 px-5 py-3.5 border-b border-slate-100 bg-slate-50/50">
        <span className="text-slate-400">{icon}</span>
        <h2 className="text-sm font-semibold text-slate-700">{title}</h2>
      </div>
      {children}
    </div>
  );
}

export default function PatientDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [records, setRecords] = useState<MedicalRecord[]>([]);
  const [bills, setBills] = useState<Bill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editOpen, setEditOpen] = useState(false);

  const load = async () => {
    try {
      const [p, a, r, b] = await Promise.all([
        patientsApi.get(+id),
        patientsApi.appointments(+id).catch(() => []),
        patientsApi.records(+id).catch(() => []),
        patientsApi.bills(+id).catch(() => []),
      ]);
      setPatient(p);
      setAppointments(a);
      setRecords(r);
      setBills(b);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  if (loading) return <PageLoader />;
  if (error) return <ErrorBanner message={error} />;
  if (!patient) return null;

  return (
    <div className="space-y-5 animate-fade-in-up">
      {/* Breadcrumb */}
      <div className="flex items-center gap-3">
        <button onClick={() => router.back()} className="w-8 h-8 flex items-center justify-center rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <h1 className="page-title">{patient.first_name} {patient.last_name}</h1>
        <button onClick={() => setEditOpen(true)} className="btn-secondary ml-auto">
          <Pencil className="w-3.5 h-3.5" /> Edit
        </button>
      </div>

      {/* Profile card */}
      <div className="card p-6">
        <div className="flex items-start gap-5">
          <div className="w-16 h-16 rounded-2xl bg-brand-100 flex items-center justify-center flex-shrink-0">
            <span className="text-xl font-bold text-brand-700">{patient.first_name[0]}{patient.last_name[0]}</span>
          </div>
          <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Date of Birth', value: formatDate(patient.date_of_birth) },
              { label: 'Age', value: calcAge(patient.date_of_birth) },
              { label: 'Gender', value: patient.gender },
              { label: 'Blood Type', value: patient.blood_group ?? '—' },
              { label: 'Phone', value: patient.phone ?? '—' },
              { label: 'Email', value: patient.email ?? '—' },
              { label: 'Emergency Contact', value: patient.emergency_contact ?? '—' },
            ].map(({ label, value }) => (
              <div key={label}>
                <p className="text-xs text-slate-400 font-medium">{label}</p>
                <p className="text-sm text-slate-800 mt-0.5 font-medium">{value}</p>
              </div>
            ))}
          </div>
        </div>
        {patient.address && (
          <p className="mt-4 text-sm text-slate-500 border-t border-slate-100 pt-4">
            <span className="font-medium text-slate-600">Address: </span>{patient.address}
          </p>
        )}
      </div>

      {/* Appointments */}
      <Section title={`Appointments (${appointments.length})`} icon={<CalendarDays className="w-4 h-4" />}>
        {appointments.length === 0 ? (
          <p className="text-sm text-slate-400 text-center py-6">No appointments</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>{['Date', 'Time', 'Doctor', 'Reason', 'Status'].map(h =>
                <th key={h} className="table-header px-4 py-2.5 text-left">{h}</th>)}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {appointments.map((a: any) => (
                <tr key={a.appointment_id} className="hover:bg-slate-50/50">
                  <td className="px-4 py-2.5">{formatDate(a.appointment_date)}</td>
                  <td className="px-4 py-2.5 text-slate-500">{a.appointment_time?.slice(0,5)}</td>
                  <td className="px-4 py-2.5">{a.doctor ? `Dr. ${a.doctor.first_name} ${a.doctor.last_name}` : `#${a.doctor_id}`}</td>
                  <td className="px-4 py-2.5 text-slate-500">{a.reason ?? '—'}</td>
                  <td className="px-4 py-2.5"><StatusBadge status={a.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Section>

      {/* Medical Records */}
      <Section title={`Medical Records (${records.length})`} icon={<FileText className="w-4 h-4" />}>
        {records.length === 0 ? (
          <p className="text-sm text-slate-400 text-center py-6">No medical records</p>
        ) : (
          <div className="divide-y divide-slate-50">
            {records.map((r: any) => (
              <div key={r.record_id} className="px-5 py-4">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-800">{r.diagnosis}</p>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {formatDate(r.record_date)} · {r.doctor ? `Dr. ${r.doctor.first_name} ${r.doctor.last_name}` : `Doctor #${r.doctor_id}`}
                    </p>
                  </div>
                </div>
                {r.treatment && <p className="mt-2 text-xs text-slate-500"><span className="font-medium">Treatment:</span> {r.treatment}</p>}
                {r.notes && <p className="mt-1 text-xs text-slate-400">{r.notes}</p>}
              </div>
            ))}
          </div>
        )}
      </Section>

      {/* Bills */}
      <Section title={`Bills (${bills.length})`} icon={<Receipt className="w-4 h-4" />}>
        {bills.length === 0 ? (
          <p className="text-sm text-slate-400 text-center py-6">No bills</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>{['Bill ID', 'Total', 'Paid', 'Balance', 'Status'].map(h =>
                <th key={h} className="table-header px-4 py-2.5 text-left">{h}</th>)}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {bills.map((b: any) => (
                <tr key={b.bill_id} className="hover:bg-slate-50/50">
                  <td className="px-4 py-2.5 text-slate-500">#{b.bill_id}</td>
                  <td className="px-4 py-2.5 font-medium">{formatCurrency(b.total_amount)}</td>
                  <td className="px-4 py-2.5 text-emerald-600">{formatCurrency(b.paid_amount)}</td>
                  <td className="px-4 py-2.5 text-red-500">{formatCurrency(b.total_amount - b.paid_amount)}</td>
                  <td className="px-4 py-2.5"><StatusBadge status={b.payment_status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Section>

      <PatientModal
        open={editOpen}
        onClose={() => setEditOpen(false)}
        patient={patient}
        onSaved={() => { setEditOpen(false); load(); }}
      />
    </div>
  );
}
