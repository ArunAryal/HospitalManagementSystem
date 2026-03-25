'use client';

import { useEffect, useState } from 'react';
import { Users, UserRound, CalendarDays, BedDouble, Receipt, TrendingUp } from 'lucide-react';
import { patientsApi, doctorsApi, appointmentsApi, billingApi } from '@/lib/api';
import { formatCurrency, formatDate } from '@/lib/utils';
import { StatCard, StatusBadge, PageLoader } from '@/components/ui';
import PatientModal from '@/components/patients/PatientModal';
import AppointmentModal from '@/components/appointments/AppointmentModal';
import MedicalRecordModal from '@/components/medical-records/MedicalRecordModal';
import AdmitPatientModal from '@/components/rooms/AdmitPatientModal';
import Link from 'next/link';

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  // Modal states
  const [patientModal, setPatientModal] = useState(false);
  const [apptModal, setApptModal] = useState(false);
  const [recordModal, setRecordModal] = useState(false);
  const [admitModal, setAdmitModal] = useState(false);
  
  const reload = async () => {
    // Only reload the relevant parts, or full reload
    const [patients, doctors, appointments, bills, rooms, admissions] = await Promise.all([
      patientsApi.list(0, 200),
      doctorsApi.list(0, 200),
      appointmentsApi.list(0, 200),
      billingApi.listBills(0, 200),
      billingApi.listRooms(0, 200),
      billingApi.listAdmissions(0, 200),
    ]);
    setData({ patients, doctors, appointments, bills, rooms, admissions });
  };

  useEffect(() => {
    Promise.allSettled([
      patientsApi.list(0, 200),
      doctorsApi.list(0, 200),
      appointmentsApi.list(0, 200),
      billingApi.listBills(0, 200),
      billingApi.listRooms(0, 200),
      billingApi.listAdmissions(0, 200),
    ]).then(([patients, doctors, appointments, bills, rooms, admissions]) => {
      setData({
        patients:    patients.status === 'fulfilled' ? patients.value : [],
        doctors:     doctors.status === 'fulfilled' ? doctors.value : [],
        appointments: appointments.status === 'fulfilled' ? appointments.value : [],
        bills:       bills.status === 'fulfilled' ? bills.value : [],
        rooms:       rooms.status === 'fulfilled' ? rooms.value : [],
        admissions:  admissions.status === 'fulfilled' ? admissions.value : [],
      });
      setLoading(false);
    });
  }, []);

  if (loading) return <PageLoader />;

  const { patients, doctors, appointments, bills, rooms, admissions } = data;
  const today = new Date().toISOString().split('T')[0];
  const todayAppts = appointments.filter((a: any) => a.appointment_date === today);
  const pendingBills = bills.filter((b: any) => b.payment_status === 'Pending');
  const totalRevenue = bills.filter((b: any) => b.payment_status === 'Paid').reduce((s: number, b: any) => s + (Number(b.total_amount) || 0), 0);
  const availableRooms = rooms.filter((r: any) => r.is_available).length;
  const recentAppointments = [...appointments].sort((a: any, b: any) =>
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  ).slice(0, 6);
  const activeAdmissions = admissions.filter((a: any) => a.status === 'Active').slice(0, 5);

  return (
    <div className="space-y-6 animate-fade-in-up">
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard label="Total Patients" value={patients.length} icon={<Users className="w-5 h-5" />} color="blue" />
        <StatCard label="Doctors" value={doctors.length} icon={<UserRound className="w-5 h-5" />} color="purple"
          sub={`${doctors.filter((d: any) => d.is_available).length} available`} />
        <StatCard label="Today's Appts" value={todayAppts.length} icon={<CalendarDays className="w-5 h-5" />} color="green" />
        <StatCard label="Available Rooms" value={availableRooms} icon={<BedDouble className="w-5 h-5" />} color="amber"
          sub={`of ${rooms.length} total`} />
        <StatCard label="Pending Bills" value={pendingBills.length} icon={<Receipt className="w-5 h-5" />} color="red" />
        <StatCard label="Revenue" value={formatCurrency(totalRevenue)} icon={<TrendingUp className="w-5 h-5" />} color="green" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        {/* Recent Appointments */}
        <div className="card">
          <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-900">Recent Appointments</h2>
            <Link href="/appointments" className="text-xs text-brand-600 hover:underline font-medium">View all →</Link>
          </div>
          <div className="divide-y divide-slate-50">
            {recentAppointments.length === 0 ? (
              <p className="text-sm text-slate-400 text-center py-8">No appointments yet</p>
            ) : recentAppointments.map((a: any) => (
              <div key={a.appointment_id} className="flex items-center justify-between px-5 py-3">
                <div>
                  <p className="text-sm font-medium text-slate-800">
                    {a.patient ? `${a.patient.first_name} ${a.patient.last_name}` : `Patient #${a.patient_id}`}
                  </p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {formatDate(a.appointment_date)} · {a.appointment_time?.slice(0, 5)}
                    {a.doctor ? ` · Dr. ${a.doctor.last_name}` : ''}
                  </p>
                </div>
                <StatusBadge status={a.status} />
              </div>
            ))}
          </div>
        </div>

        {/* Active Admissions */}
        <div className="card">
          <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-900">Active Admissions</h2>
            <Link href="/rooms" className="text-xs text-brand-600 hover:underline font-medium">View all →</Link>
          </div>
          <div className="divide-y divide-slate-50">
            {activeAdmissions.length === 0 ? (
              <p className="text-sm text-slate-400 text-center py-8">No active admissions</p>
            ) : activeAdmissions.map((a: any) => (
              <div key={a.admission_id} className="flex items-center justify-between px-5 py-3">
                <div>
                  <p className="text-sm font-medium text-slate-800">
                    {a.patient ? `${a.patient.first_name} ${a.patient.last_name}` : `Patient #${a.patient_id}`}
                  </p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {a.diagnosis} · Room {a.room?.room_number ?? a.room_id}
                  </p>
                </div>
                <StatusBadge status={a.status} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Links */}
      <div className="card px-5 py-4">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Quick Actions</p>
        <div className="flex flex-wrap gap-2">
          <button className="btn-secondary text-xs py-1.5" onClick={() => setPatientModal(true)}>+ New Patient</button>
          <button className="btn-secondary text-xs py-1.5" onClick={() => setApptModal(true)}>+ Book Appointment</button>
          <button className="btn-secondary text-xs py-1.5" onClick={() => setRecordModal(true)}>+ Medical Record</button>
          <button className="btn-secondary text-xs py-1.5" onClick={() => setAdmitModal(true)}>+ Admit Patient</button>
        </div>
      </div>

      {/* Modals */}
      <PatientModal open={patientModal} onClose={() => setPatientModal(false)} patient={null} onSaved={() => { setPatientModal(false); reload(); }} />
      <AppointmentModal open={apptModal} onClose={() => setApptModal(false)} appointment={null} onSaved={() => { setApptModal(false); reload(); }} />
      <MedicalRecordModal open={recordModal} onClose={() => setRecordModal(false)} record={null} onSaved={() => { setRecordModal(false); reload(); }} />
      <AdmitPatientModal open={admitModal} onClose={() => setAdmitModal(false)} onSaved={() => { setAdmitModal(false); reload(); }} />
    </div>
  );
}
