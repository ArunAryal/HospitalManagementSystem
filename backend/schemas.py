from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime, time
from typing import Optional
from decimal import Decimal


# ─── Patient Schemas ─────────────────────────────────────────────────────────
class PatientBase(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    date_of_birth: date
    gender: str = Field(..., pattern="^(Male|Female|Other)$")
    blood_group: Optional[str] = Field(None, max_length=5)
    phone: str = Field(..., max_length=15)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, max_length=15)


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, max_length=15)


class PatientShort(BaseModel):
    patient_id: int
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class Patient(PatientBase):
    patient_id: int
    registration_date: datetime

    class Config:
        from_attributes = True


# ─── Doctor Schemas ─────────────────────────────────────────────────────────
class DoctorBase(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    specialization: str = Field(..., max_length=100)
    qualification: Optional[str] = Field(None, max_length=200)
    phone: str = Field(..., max_length=15)
    email: EmailStr
    consultation_fee: Decimal = Field(..., gt=0)
    experience_years: Optional[int] = Field(None, ge=0)
    joined_date: date


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    specialization: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    consultation_fee: Optional[Decimal] = Field(None, gt=0)
    is_available: Optional[bool] = None


class DoctorShort(BaseModel):
    doctor_id: int
    first_name: str
    last_name: str
    specialization: str

    class Config:
        from_attributes = True


class Doctor(DoctorBase):
    doctor_id: int
    is_available: bool

    class Config:
        from_attributes = True


# ─── Appointment Schemas ────────────────────────────────────────────────────
class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    reason: Optional[str] = None
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    status: Optional[str] = Field(
        None, pattern="^(Scheduled|Completed|Cancelled|No-Show)$"
    )
    notes: Optional[str] = None


class Appointment(AppointmentBase):
    appointment_id: int
    status: str
    created_at: datetime
    patient: Optional[PatientShort] = None
    doctor: Optional[DoctorShort] = None

    class Config:
        from_attributes = True


# ─── Medical Record Schemas
class MedicalRecordBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    diagnosis: str
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None


class MedicalRecordUpdate(BaseModel):
    diagnosis: Optional[str] = None
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None


class MedicalRecordCreate(MedicalRecordBase):
    pass


class MedicalRecord(MedicalRecordBase):
    record_id: int
    record_date: datetime
    patient: Optional[PatientShort] = None
    doctor: Optional[DoctorShort] = None

    class Config:
        from_attributes = True


# Medicine Schemas
class MedicineBase(BaseModel):
    medicine_name: str = Field(..., max_length=100)
    description: Optional[str] = None
    manufacturer: Optional[str] = Field(None, max_length=100)
    unit_price: Decimal = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)
    reorder_level: int = Field(default=10, ge=0)
    expiry_date: Optional[date] = None


class MedicineCreate(MedicineBase):
    pass


class MedicineUpdate(BaseModel):
    unit_price: Optional[Decimal] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    reorder_level: Optional[int] = Field(None, ge=0)


class Medicine(MedicineBase):
    medicine_id: int

    class Config:
        from_attributes = True


# Prescription Schemas
class PrescriptionBase(BaseModel):
    medical_record_id: int
    medicine_id: int
    dosage: str = Field(..., max_length=100)
    frequency: str = Field(..., max_length=50)
    duration: str = Field(..., max_length=50)
    quantity: int = Field(..., gt=0)
    instructions: Optional[str] = None


class PrescriptionCreate(PrescriptionBase):
    pass


class Prescription(PrescriptionBase):
    prescription_id: int

    class Config:
        from_attributes = True


# Room Schemas
class RoomBase(BaseModel):
    room_number: str = Field(..., max_length=10)
    room_type: str = Field(..., pattern="^(General|Private|ICU|Emergency)$")
    capacity: int = Field(..., gt=0)
    charge_per_day: Decimal = Field(..., gt=0)


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    room_number: Optional[str] = Field(None, max_length=10)
    room_type: Optional[str] = Field(None, pattern="^(General|Private|ICU|Emergency)$")
    capacity: Optional[int] = Field(None, gt=0)
    charge_per_day: Optional[Decimal] = Field(None, gt=0)
    is_available: Optional[bool] = None
    current_occupancy: Optional[int] = Field(None, ge=0)


class Room(RoomBase):
    room_id: int
    current_occupancy: int
    is_available: bool

    class Config:
        from_attributes = True
        ignored_types = (object,)


# ─── Admission Schemas
class AdmissionBase(BaseModel):
    patient_id: int
    room_id: int
    doctor_id: int
    admission_date: datetime
    reason: str


class AdmissionCreate(AdmissionBase):
    pass


class AdmissionUpdate(BaseModel):
    discharge_date: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(Active|Discharged)$")


class Admission(AdmissionBase):
    admission_id: int
    discharge_date: Optional[datetime] = None
    status: str
    patient: Optional[PatientShort] = None
    doctor: Optional[DoctorShort] = None

    class Config:
        from_attributes = True


# Bill Schemas
class BillBase(BaseModel):
    patient_id: int
    admission_id: Optional[int] = None
    appointment_id: Optional[int] = None
    consultation_fee: Decimal = Field(default=0, ge=0)
    medicine_charges: Decimal = Field(default=0, ge=0)
    room_charges: Decimal = Field(default=0, ge=0)
    other_charges: Decimal = Field(default=0, ge=0)
    total_amount: Decimal = Field(..., ge=0)


class BillCreate(BillBase):
    pass


class BillUpdate(BaseModel):
    payment_status: Optional[str] = Field(
        None, pattern="^(Pending|Paid|Partially Paid)$"
    )
    payment_method: Optional[str] = Field(
        None, pattern="^(Cash|Card|Insurance|Online)$"
    )
    paid_amount: Optional[Decimal] = Field(None, ge=0)


class Bill(BillBase):
    bill_id: int
    payment_status: str
    payment_method: Optional[str] = None
    bill_date: datetime
    paid_amount: Decimal
    patient: Optional[PatientShort] = None

    class Config:
        from_attributes = True
