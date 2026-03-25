// ─── Patient ────────────────────────────────────────────────────────────────
export type Gender = 'Male' | 'Female' | 'Other';
export type BloodType = 'A+' | 'A-' | 'B+' | 'B-' | 'AB+' | 'AB-' | 'O+' | 'O-';

export interface Patient {
  patient_id: number;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: Gender;
  blood_group?: string;
  phone: string;
  email?: string;
  address?: string;
  emergency_contact?: string;
  registration_date: string;
}

export interface PatientCreate {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: Gender;
  blood_group?: string;
  phone: string;
  email?: string;
  address?: string;
  emergency_contact?: string;
}

// ─── Doctor ─────────────────────────────────────────────────────────────────
export interface Doctor {
  doctor_id: number;
  first_name: string;
  last_name: string;
  specialization: string;
  phone: string;
  email: string;
  consultation_fee: number;
  experience_years?: number;
  joined_date: string;
  is_available: boolean;
}

export interface DoctorCreate {
  first_name: string;
  last_name: string;
  specialization: string;
  qualification?: string;
  phone: string;
  email: string;
  consultation_fee: number;
  experience_years?: number;
  joined_date: string;
  is_available?: boolean;
}

// ─── Appointment ─────────────────────────────────────────────────────────────
export type AppointmentStatus = 'Scheduled' | 'Completed' | 'Cancelled' | 'No-Show';

export interface Appointment {
  appointment_id: number;
  patient_id: number;
  doctor_id: number;
  appointment_date: string;
  appointment_time: string;
  status: AppointmentStatus;
  reason?: string;
  notes?: string;
  patient?: Patient;
  doctor?: Doctor;
  created_at: string;
}

export interface AppointmentCreate {
  patient_id: number;
  doctor_id: number;
  appointment_date: string;
  appointment_time: string;
  reason?: string;
  notes?: string;
}

// ─── Medical Record ──────────────────────────────────────────────────────────
export interface MedicalRecord {
  record_id: number;
  patient_id: number;
  doctor_id: number;
  record_date: string;
  diagnosis: string;
  treatment?: string;
  notes?: string;
  patient?: Patient;
  doctor?: Doctor;
  created_at: string;
}

export interface MedicalRecordCreate {
  patient_id: number;
  doctor_id: number;
  record_date: string;
  diagnosis: string;
  treatment?: string;
  notes?: string;
}

// ─── Medicine & Prescription ─────────────────────────────────────────────────
export interface Medicine {
  medicine_id: number;
  medicine_name: string;
  description?: string;
  manufacturer?: string;
  unit_price: number;
  stock_quantity: number;
  created_at: string;
}

export interface MedicineCreate {
  medicine_name: string;
  description?: string;
  manufacturer?: string;
  unit_price: number;
  stock_quantity: number;
}

export interface Prescription {
  prescription_id: number;
  record_id: number;
  medicine_id: number;
  dosage: string;
  frequency: string;
  duration: string;
  notes?: string;
  medicine?: Medicine;
  created_at: string;
}

export interface PrescriptionCreate {
  record_id: number;
  medicine_id: number;
  dosage: string;
  frequency: string;
  duration: string;
  notes?: string;
}

// ─── Room & Admission ────────────────────────────────────────────────────────
export type RoomType = 'General' | 'Private' | 'ICU' | 'Emergency' | 'Operation';
export type RoomStatus = 'Available' | 'Occupied' | 'Maintenance';

export interface Room {
  room_id: number;
  room_number: string;
  room_type: RoomType;
  capacity: number;
  current_occupancy: number;
  charge_per_day: number;
  is_available: boolean;
}

export interface Admission {
  admission_id: number;
  patient_id: number;
  room_id: number;
  doctor_id: number;
  admission_date: string;
  discharge_date?: string;
  reason: string;
  status: 'Active' | 'Discharged';
  patient?: Patient;
  room?: Room;
  doctor?: Doctor;
  created_at: string;
}

export interface AdmissionCreate {
  patient_id: number;
  room_id: number;
  doctor_id: number;
  admission_date: string;
  reason: string;
}

// ─── Billing ─────────────────────────────────────────────────────────────────
export type BillStatus = 'Pending' | 'Paid' | 'Partially Paid' | 'Cancelled';
export type PaymentMethod = 'Cash' | 'Card' | 'Insurance' | 'Online';

export interface Bill {
  bill_id: number;
  patient_id: number;
  admission_id?: number;
  appointment_id?: number;
  total_amount: number;
  paid_amount: number;
  payment_status: BillStatus;
  payment_method?: PaymentMethod;
  bill_date: string;
  patient?: Patient;
}

export interface BillCreate {
  patient_id: number;
  admission_id?: number;
  appointment_id?: number;
  total_amount: number;
  bill_date?: string;
  consultation_fee?: number;
  medicine_charges?: number;
  room_charges?: number;
  other_charges?: number;
}

export interface Payment {
  payment_id: number;
  bill_id: number;
  amount: number;
  payment_method: PaymentMethod;
  payment_date: string;
  notes?: string;
}

export interface PaymentCreate {
  bill_id: number;
  amount: number;
  payment_method: PaymentMethod;
  notes?: string;
}

// ─── Shared ──────────────────────────────────────────────────────────────────
export interface ApiError {
  detail: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}
