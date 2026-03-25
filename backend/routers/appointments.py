from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from typing import Optional
from datetime import date
from ..database import get_db
from .. import models
from .. import schemas

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.get("/", response_model=list[schemas.Appointment])
def list_appointments(
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    appointment_date: Optional[date] = None,
    status: Optional[str] = Query(None, pattern="^(Scheduled|Completed|Cancelled|No-Show)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(models.Appointment).options(
        selectinload(models.Appointment.patient),
        selectinload(models.Appointment.doctor)
    )
    if patient_id:
        query = query.filter(models.Appointment.patient_id == patient_id)
    if doctor_id:
        query = query.filter(models.Appointment.doctor_id == doctor_id)
    if appointment_date:
        query = query.filter(models.Appointment.appointment_date == appointment_date)
    if status:
        query = query.filter(models.Appointment.status == models.AppointmentStatus(status))
    return query.order_by(models.Appointment.appointment_date, models.Appointment.appointment_time).offset(skip).limit(limit).all()


@router.post("/", response_model=schemas.Appointment, status_code=201)
def create_appointment(appt: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.patient_id == appt.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == appt.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if not doctor.is_available:
        raise HTTPException(status_code=400, detail="Doctor is not available")

    # Check for conflicting appointment at same date+time
    conflict = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == appt.doctor_id,
        models.Appointment.appointment_date == appt.appointment_date,
        models.Appointment.appointment_time == appt.appointment_time,
        models.Appointment.status == models.AppointmentStatus.Scheduled,
    ).first()
    if conflict:
        raise HTTPException(status_code=409, detail="Doctor already has an appointment at this date and time")

    db_appt = models.Appointment(**appt.model_dump())
    db.add(db_appt)
    db.commit()
    db.refresh(db_appt)
    
    # Create bill for appointment with consultation fee
    consultation_fee = doctor.consultation_fee if doctor else 0
    db_bill = models.Bill(
        patient_id=appt.patient_id,
        appointment_id=db_appt.appointment_id,
        consultation_fee=consultation_fee,
        medicine_charges=0,
        room_charges=0,
        other_charges=0,
        total_amount=consultation_fee,
    )
    db.add(db_bill)
    db.commit()
    
    return db_appt


@router.get("/{appointment_id}", response_model=schemas.Appointment)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = db.query(models.Appointment).filter(models.Appointment.appointment_id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


@router.put("/{appointment_id}", response_model=schemas.Appointment)
def update_appointment(
    appointment_id: int, update: schemas.AppointmentUpdate, db: Session = Depends(get_db)
):
    appt = db.query(models.Appointment).filter(models.Appointment.appointment_id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    data = update.model_dump(exclude_unset=True)

    # Convert string status to enum
    if "status" in data:
        status_map = {
            "Scheduled": models.AppointmentStatus.Scheduled,
            "Completed": models.AppointmentStatus.Completed,
            "Cancelled": models.AppointmentStatus.Cancelled,
            "No-Show": models.AppointmentStatus.NoShow,
        }
        data["status"] = status_map[data["status"]]

    for field, value in data.items():
        setattr(appt, field, value)
    db.commit()
    db.refresh(appt)
    
    # Update or remove bill when appointment status changes
    bill = db.query(models.Bill).filter(
        models.Bill.appointment_id == appointment_id
    ).first()
    
    if bill:
        # If appointment is Cancelled or No-Show, clear the consultation fee
        if appt.status in [models.AppointmentStatus.Cancelled, models.AppointmentStatus.NoShow]:
            bill.consultation_fee = 0
            bill.total_amount = bill.medicine_charges + bill.room_charges + bill.other_charges
        db.commit()
    
    return appt


@router.delete("/{appointment_id}", status_code=204)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = db.query(models.Appointment).filter(models.Appointment.appointment_id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(appt)
    db.commit()