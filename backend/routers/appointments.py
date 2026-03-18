from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from backend.database import get_db
from backend import models, schemas

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

@router.post("/", response_model=schemas.Appointment, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    """Create a new appointment"""
    # Verify patient exists
    patient = db.query(models.Patient).filter(models.Patient.patient_id == appointment.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Verify doctor exists
    doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == appointment.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check if doctor is available
    if not doctor.is_available:
        raise HTTPException(status_code=400, detail="Doctor is not available")
    
    # Check for conflicting appointments
    conflict = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == appointment.doctor_id,
        models.Appointment.appointment_date == appointment.appointment_date,
        models.Appointment.appointment_time == appointment.appointment_time,
        models.Appointment.status != "Cancelled"
    ).first()
    
    if conflict:
        raise HTTPException(status_code=400, detail="This time slot is already booked")
    
    db_appointment = models.Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.get("/", response_model=List[schemas.Appointment])
def get_appointments(
    skip: int = 0, 
    limit: int = 100, 
    appointment_date: date = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get all appointments, optionally filter by date and status"""
    query = db.query(models.Appointment)
    
    if appointment_date:
        query = query.filter(models.Appointment.appointment_date == appointment_date)
    
    if status:
        query = query.filter(models.Appointment.status == status)
    
    appointments = query.offset(skip).limit(limit).all()
    return appointments

@router.get("/{appointment_id}", response_model=schemas.Appointment)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Get a specific appointment by ID"""
    appointment = db.query(models.Appointment).filter(
        models.Appointment.appointment_id == appointment_id
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.put("/{appointment_id}", response_model=schemas.Appointment)
def update_appointment(
    appointment_id: int, 
    appointment_update: schemas.AppointmentUpdate, 
    db: Session = Depends(get_db)
):
    """Update appointment information"""
    db_appointment = db.query(models.Appointment).filter(
        models.Appointment.appointment_id == appointment_id
    ).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # If rescheduling, check for conflicts
    if appointment_update.appointment_date or appointment_update.appointment_time:
        new_date = appointment_update.appointment_date or db_appointment.appointment_date
        new_time = appointment_update.appointment_time or db_appointment.appointment_time
        
        conflict = db.query(models.Appointment).filter(
            models.Appointment.doctor_id == db_appointment.doctor_id,
            models.Appointment.appointment_date == new_date,
            models.Appointment.appointment_time == new_time,
            models.Appointment.appointment_id != appointment_id,
            models.Appointment.status != models.AppointmentStatus.Cancelled
        ).first()
        
        if conflict:
            raise HTTPException(status_code=400, detail="This time slot is already booked")
    
    update_data = appointment_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_appointment, key, value)
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Delete an appointment"""
    db_appointment = db.query(models.Appointment).filter(
        models.Appointment.appointment_id == appointment_id
    ).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    db.delete(db_appointment)
    db.commit()
    return None

@router.get("/today/list", response_model=List[schemas.Appointment])
def get_today_appointments(db: Session = Depends(get_db)):
    """Get all appointments for today"""
    from datetime import date
    today = date.today()
    appointments = db.query(models.Appointment).filter(
        models.Appointment.appointment_date == today,
        models.Appointment.status != models.AppointmentStatus.Cancelled
    ).all()
    return appointments
