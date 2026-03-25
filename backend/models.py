from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Boolean, DECIMAL, Enum, ForeignKey, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base
import enum

class GenderEnum(enum.Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"

class AppointmentStatus(enum.Enum):
    Scheduled = "Scheduled"
    Completed = "Completed"
    Cancelled = "Cancelled"
    NoShow = "No-Show"

class RoomType(enum.Enum):
    General = "General"
    Private = "Private"
    ICU = "ICU"
    Emergency = "Emergency"

class PaymentStatus(enum.Enum):
    Pending = "Pending"
    Paid = "Paid"
    PartiallyPaid = "Partially Paid"

class PaymentMethod(enum.Enum):
    Cash = "Cash"
    Card = "Card"
    Insurance = "Insurance"
    Online = "Online"

class Patient(Base):
    __tablename__ = "patients"
    
    patient_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    blood_group = Column(String(5))
    phone = Column(String(15), nullable=False, index=True)
    email = Column(String(100))
    address = Column(Text)
    emergency_contact = Column(String(15))
    registration_date = Column(DateTime, default=datetime.utcnow)
    
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
    admissions = relationship("Admission", back_populates="patient", cascade="all, delete-orphan")
    bills = relationship("Bill", back_populates="patient", cascade="all, delete-orphan")

class Doctor(Base):
    __tablename__ = "doctors"
    
    doctor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    specialization = Column(String(100), nullable=False, index=True)
    qualification = Column(String(200))
    phone = Column(String(15), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    consultation_fee = Column(DECIMAL(10, 2), nullable=False)
    experience_years = Column(Integer)
    joined_date = Column(Date, nullable=False)
    is_available = Column(Boolean, default=True)
    
    appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")
    medical_records = relationship("MedicalRecord", back_populates="doctor", cascade="all, delete-orphan")
    admissions = relationship("Admission", back_populates="doctor", cascade="all, delete-orphan")

class Appointment(Base):
    __tablename__ = "appointments"
    
    appointment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=False)
    appointment_date = Column(Date, nullable=False, index=True)
    appointment_time = Column(Time, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.Scheduled, index=True)
    reason = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    medical_records = relationship("MedicalRecord", back_populates="appointment", cascade="all, delete-orphan")
    bills = relationship("Bill", back_populates="appointment", cascade="all, delete-orphan")

class MedicalRecord(Base):
    __tablename__ = "medical_records"
    
    record_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.appointment_id"))
    diagnosis = Column(Text, nullable=False)
    symptoms = Column(Text)
    treatment = Column(Text)
    notes = Column(Text)
    record_date = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("Doctor", back_populates="medical_records")
    appointment = relationship("Appointment", back_populates="medical_records")
    prescriptions = relationship("Prescription", back_populates="medical_record", cascade="all, delete-orphan")

class Medicine(Base):
    __tablename__ = "medicines"
    
    medicine_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    medicine_name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    manufacturer = Column(String(100))
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, default=10)
    expiry_date = Column(Date)
    
    prescriptions = relationship("Prescription", back_populates="medicine", cascade="all, delete-orphan")

class Prescription(Base):
    __tablename__ = "prescriptions"
    
    prescription_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    medical_record_id = Column(Integer, ForeignKey("medical_records.record_id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.medicine_id"), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(50), nullable=False)
    duration = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    instructions = Column(Text)
    
    medical_record = relationship("MedicalRecord", back_populates="prescriptions")
    medicine = relationship("Medicine", back_populates="prescriptions")

class Room(Base):
    __tablename__ = "rooms"
    
    room_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_number = Column(String(10), unique=True, nullable=False)
    room_type = Column(Enum(RoomType), nullable=False)
    capacity = Column(Integer, nullable=False)
    current_occupancy = Column(Integer, default=0)
    charge_per_day = Column(DECIMAL(10, 2), nullable=False)
    is_available = Column(Boolean, default=True)
    
    admissions = relationship("Admission", back_populates="room", cascade="all, delete-orphan")

class Admission(Base):
    __tablename__ = "admissions"
    
    admission_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.room_id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=False)
    admission_date = Column(DateTime, nullable=False)
    discharge_date = Column(DateTime)
    reason = Column(Text, nullable=False)
    status = Column(String(20), default="Active")
    
    patient = relationship("Patient", back_populates="admissions")
    room = relationship("Room", back_populates="admissions")
    doctor = relationship("Doctor", back_populates="admissions")
    bills = relationship("Bill", back_populates="admission", cascade="all, delete-orphan")

class Bill(Base):
    __tablename__ = "bills"
    
    bill_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    admission_id = Column(Integer, ForeignKey("admissions.admission_id"))
    appointment_id = Column(Integer, ForeignKey("appointments.appointment_id"))
    consultation_fee = Column(DECIMAL(10, 2), default=0)
    medicine_charges = Column(DECIMAL(10, 2), default=0)
    room_charges = Column(DECIMAL(10, 2), default=0)
    other_charges = Column(DECIMAL(10, 2), default=0)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.Pending)
    payment_method = Column(Enum(PaymentMethod))
    bill_date = Column(DateTime, default=datetime.utcnow)
    paid_amount = Column(DECIMAL(10, 2), default=0)
    
    patient = relationship("Patient", back_populates="bills")
    admission = relationship("Admission", back_populates="bills")
    appointment = relationship("Appointment", back_populates="bills")
