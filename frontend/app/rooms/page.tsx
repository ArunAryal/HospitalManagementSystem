'use client';

import { useEffect, useState } from 'react';
import { Plus, BedDouble, Pencil, LogOut } from 'lucide-react';
import { billingApi, patientsApi, doctorsApi } from '@/lib/api';
import { Room, Admission, Patient, Doctor, RoomType, RoomStatus, AdmissionCreate } from '@/types';
import { formatDate, formatCurrency } from '@/lib/utils';
import { PageLoader, ErrorBanner, StatusBadge, Modal, Field, Spinner, SearchInput } from '@/components/ui';

type Tab = 'rooms' | 'admissions';

const ROOM_TYPES: RoomType[] = ['General', 'Private', 'ICU', 'Emergency', 'Operation'];
const ROOM_STATUSES: RoomStatus[] = ['Available', 'Partially Occupied', 'Fully Occupied', 'Maintenance'];

export default function RoomsPage() {
  const [tab, setTab] = useState<Tab>('rooms');
  const [rooms, setRooms] = useState<Room[]>([]);
  const [admissions, setAdmissions] = useState<Admission[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [roomModal, setRoomModal] = useState(false);
  const [editRoom, setEditRoom] = useState<Room | null>(null);
  const [admitModal, setAdmitModal] = useState(false);
  const [roomForm, setRoomForm] = useState<any>({ room_number: '', room_type: 'General', capacity: 1, charge_per_day: 0, is_available: true });
  const [admitForm, setAdmitForm] = useState<AdmissionCreate>({ patient_id: 0, room_id: 0, doctor_id: 0, admission_date: new Date().toISOString().split('T')[0], reason: '' });
  const [saving, setSaving] = useState(false);
  const [search, setSearch] = useState('');

  const load = async () => {
    try {
      const [r, a, p, d] = await Promise.all([
        billingApi.listRooms(0, 500),
        billingApi.listAdmissions(0, 500),
        patientsApi.list(0, 500),
        doctorsApi.list(0, 500),
      ]);
      setRooms(r); setAdmissions(a); setPatients(p); setDoctors(d);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  useEffect(() => {
    if (editRoom) {
      const { room_id, current_occupancy, ...rest } = editRoom as any;
      setRoomForm(rest);
    } else {
      setRoomForm({ room_number: '', room_type: 'General', capacity: 1, charge_per_day: 0, is_available: true });
    }
  }, [editRoom, roomModal]);

  useEffect(() => {
    if (!admitModal) {
      setAdmitForm({ patient_id: 0, room_id: 0, doctor_id: 0, admission_date: new Date().toISOString().split('T')[0], reason: '' });
      setError('');
    }
  }, [admitModal]);

  const saveRoom = async () => {
    setSaving(true);
    try {
      if (editRoom) {
        await billingApi.updateRoom(editRoom.room_id, roomForm);
      } else {
        await billingApi.createRoom(roomForm);
      }
      setRoomModal(false);
      load();
    } catch (e: any) { setError(e.message); }
    finally { setSaving(false); }
  };

  const admitPatient = async () => {
    if (!admitForm.patient_id || !admitForm.room_id || !admitForm.doctor_id || !admitForm.reason) {
      setError('Please fill all required fields');
      return;
    }
    setSaving(true);
    try {
      await billingApi.createAdmission(admitForm);
      setAdmitModal(false);
      load();
    } catch (e: any) { setError(e.message); }
    finally { setSaving(false); }
  };

  const discharge = async (id: number) => {
    try {
      await billingApi.discharge(id, { discharge_date: new Date().toISOString().split('T')[0] });
      load();
    } catch (e: any) { setError(e.message); }
  };

  if (loading) return <PageLoader />;

  const filteredRooms = rooms.filter(r => {
    const q = search.toLowerCase();
    return r.room_number.toLowerCase().includes(q) || r.room_type.toLowerCase().includes(q);
  });
  const filteredAdmissions = admissions.filter(a => {
    const q = search.toLowerCase();
    return (a as any).patient ? `${(a as any).patient.first_name} ${(a as any).patient.last_name}`.toLowerCase().includes(q) : true;
  });

  const TYPE_COLORS: Record<string, string> = {
    General: 'bg-slate-100 text-slate-600', Private: 'bg-purple-50 text-purple-700',
    ICU: 'bg-red-50 text-red-700', Emergency: 'bg-orange-50 text-orange-700',
    Operation: 'bg-blue-50 text-blue-700',
  };

  return (
    <div className="space-y-4 animate-fade-in-up">
      {error && <ErrorBanner message={error} />}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Rooms & Admissions</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {rooms.filter(r => r.current_occupancy === 0).length} available · {rooms.filter(r => r.current_occupancy > 0 && r.current_occupancy < r.capacity).length} partially occupied · {rooms.filter(r => r.current_occupancy >= r.capacity).length} fully occupied · {admissions.filter(a => a.status === 'Active').length} active admissions
          </p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary" onClick={() => { setEditRoom(null); setRoomModal(true); }}>
            <Plus className="w-4 h-4" /> Add Room
          </button>
          <button className="btn-primary" onClick={() => setAdmitModal(true)}>
            <Plus className="w-4 h-4" /> Admit Patient
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 p-1 rounded-xl w-fit">
        {(['rooms', 'admissions'] as Tab[]).map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-1.5 text-sm font-medium rounded-lg transition-colors capitalize ${tab === t ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>
            {t}
          </button>
        ))}
      </div>

      <div className="card px-4 py-3 flex items-center gap-3">
        <SearchInput value={search} onChange={setSearch} placeholder={tab === 'rooms' ? 'Search rooms…' : 'Search admissions…'} />
      </div>

      {tab === 'rooms' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filteredRooms.map(r => (
            <div key={r.room_id} className="card p-5">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-lg font-bold text-slate-900">{r.room_number}</p>
                    <span className={`badge text-xs ${TYPE_COLORS[r.room_type]}`}>{r.room_type}</span>
                  </div>
                  <StatusBadge status={r.current_occupancy === 0 ? 'Available' : (r.current_occupancy >= r.capacity ? 'Fully Occupied' : 'Partially Occupied')} />
                </div>
                <button onClick={() => { setEditRoom(r); setRoomModal(true); }}
                  className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100">
                  <Pencil className="w-3.5 h-3.5" />
                </button>
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div><p className="text-slate-400">Capacity</p><p className="font-semibold text-slate-700 mt-0.5">{r.capacity}</p></div>
                <div><p className="text-slate-400">Occupied</p><p className="font-semibold text-slate-700 mt-0.5">{r.current_occupancy}</p></div>
                <div><p className="text-slate-400">Daily Rate</p><p className="font-semibold text-slate-700 mt-0.5">{formatCurrency(r.charge_per_day)}</p></div>
              </div>
              {r.current_occupancy < r.capacity && (
                <button className="btn-primary w-full mt-3 text-xs justify-center py-1.5"
                  onClick={() => { setAdmitForm(f => ({ ...f, room_id: r.room_id })); setAdmitModal(true); }}>
                  Admit Patient
                </button>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-100">
              <tr>{['Patient', 'Room', 'Doctor', 'Reason', 'Admitted', 'Status', ''].map(h =>
                <th key={h} className="table-header px-4 py-3 text-left">{h}</th>)}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {filteredAdmissions.map((a: any) => (
                <tr key={a.admission_id} className="hover:bg-slate-50/60">
                  <td className="px-4 py-3 font-medium">{a.patient ? `${a.patient.first_name} ${a.patient.last_name}` : `#${a.patient_id}`}</td>
                  <td className="px-4 py-3 text-slate-500">{a.room?.room_number ?? `#${a.room_id}`}</td>
                  <td className="px-4 py-3 text-slate-500">{a.doctor ? `Dr. ${a.doctor.last_name}` : `#${a.doctor_id}`}</td>
                  <td className="px-4 py-3 text-slate-500 max-w-[160px] truncate">{a.reason}</td>
                  <td className="px-4 py-3 text-xs text-slate-400">{formatDate(a.admission_date)}</td>
                  <td className="px-4 py-3"><StatusBadge status={a.status} /></td>
                  <td className="px-4 py-3">
                    {a.status === 'Active' && (
                      <button onClick={() => discharge(a.admission_id)}
                        className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-800 px-2 py-1 rounded-lg hover:bg-slate-100">
                        <LogOut className="w-3 h-3" /> Discharge
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Room Modal */}
      <Modal open={roomModal} onClose={() => setRoomModal(false)} title={editRoom ? 'Edit Room' : 'Add Room'} size="lg">
        <div className="grid grid-cols-3 gap-3">
          <Field label="Room Number" required>
            <input className="input" value={roomForm.room_number} onChange={e => setRoomForm((f: any) => ({ ...f, room_number: e.target.value }))} />
          </Field>
          <Field label="Room Type">
            <select className="input" value={roomForm.room_type} onChange={e => setRoomForm((f: any) => ({ ...f, room_type: e.target.value }))}>
              {ROOM_TYPES.map(t => <option key={t}>{t}</option>)}
            </select>
          </Field>
          <Field label="Capacity">
            <input type="number" min="1" className="input" value={roomForm.capacity || ''} onChange={e => setRoomForm((f: any) => ({ ...f, capacity: e.target.value ? +e.target.value : 0 }))} />
          </Field>
          <Field label="Daily Rate ($)">
            <input type="number" min="0" step="0.01" className="input" value={roomForm.charge_per_day || ''} onChange={e => setRoomForm((f: any) => ({ ...f, charge_per_day: e.target.value ? +e.target.value : 0 }))} />
          </Field>
          <Field label="Available">
            <select className="input" value={roomForm.is_available ? 'true' : 'false'} onChange={e => setRoomForm((f: any) => ({ ...f, is_available: e.target.value === 'true' }))}>
              <option value="true">Yes</option>
              <option value="false">No</option>
            </select>
          </Field>
        </div>
        <div className="flex justify-end gap-2 mt-4">
          <button className="btn-secondary" onClick={() => setRoomModal(false)}>Cancel</button>
          <button className="btn-primary" onClick={saveRoom} disabled={saving}>{saving && <Spinner size="sm" />}{editRoom ? 'Save' : 'Add Room'}</button>
        </div>
      </Modal>

      {/* Admit Modal */}
      <Modal open={admitModal} onClose={() => setAdmitModal(false)} title="Admit Patient" size="lg">
        {error && <div className="mb-3"><ErrorBanner message={error} /></div>}
        <div className="grid grid-cols-3 gap-3">
          <Field label="Patient" required>
            <select className="input" value={admitForm.patient_id} onChange={e => setAdmitForm(f => ({ ...f, patient_id: +e.target.value }))}>
              <option value={0}>— Select —</option>
              {patients.map(p => <option key={p.patient_id} value={p.patient_id}>{p.first_name} {p.last_name}</option>)}
            </select>
          </Field>
          <Field label="Room" required>
            <select className="input" value={admitForm.room_id} onChange={e => setAdmitForm(f => ({ ...f, room_id: +e.target.value }))}>
              <option value={0}>— Select —</option>
              {rooms.filter(r => r.current_occupancy < r.capacity).map(r => <option key={r.room_id} value={r.room_id}>{r.room_number} ({r.room_type})</option>)}
            </select>
          </Field>
          <Field label="Doctor" required>
            <select className="input" value={admitForm.doctor_id} onChange={e => setAdmitForm(f => ({ ...f, doctor_id: +e.target.value }))}>
              <option value={0}>— Select —</option>
              {doctors.map(d => <option key={d.doctor_id} value={d.doctor_id}>Dr. {d.first_name} {d.last_name}</option>)}
            </select>
          </Field>
          <Field label="Admission Date" required>
            <input type="date" className="input" value={admitForm.admission_date} onChange={e => setAdmitForm(f => ({ ...f, admission_date: e.target.value }))} />
          </Field>
          <div className="col-span-2">
            <Field label="Reason" required>
              <input className="input" value={admitForm.reason} onChange={e => setAdmitForm(f => ({ ...f, reason: e.target.value }))} />
            </Field>
          </div>
        </div>
        <div className="flex justify-end gap-2 mt-4">
          <button className="btn-secondary" onClick={() => setAdmitModal(false)}>Cancel</button>
          <button className="btn-primary" onClick={admitPatient} disabled={saving}>{saving && <Spinner size="sm" />}Admit Patient</button>
        </div>
      </Modal>
    </div>
  );
}
