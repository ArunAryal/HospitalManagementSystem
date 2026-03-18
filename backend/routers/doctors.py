from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend import models, schemas

router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)

@router.post("/", response_model=schemas.Doctor, status_code=status.HTTP_201_CREATED)
def create_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    """Create a new doctor"""
    # Check if email already exists
    existing_doctor = db.query(models.Doctor).filter(models.Doctor.email == doctor.email).first()
    if existing_doctor:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_doctor = models.Doctor(**doctor.dict())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

@router.get("/", response_model=List[schemas.Doctor])
def get_doctors(skip: int = 0, limit: int = 100, specialization: str = None, db: Session = Depends(get_db)):
    """Get all doctors, optionally filter by specialization"""
    query = db.query(models.Doctor)
    
    if specialization:
        query = query.filter(models.Doctor.specialization == specialization)
    
    doctors = query.offset(skip).limit(limit).all()
    return doctors

@router.get("/specializations/list")
def get_specializations(db: Session = Depends(get_db)):
    """Get list of all unique specializations"""
    specializations = db.query(models.Doctor.specialization).distinct().all()
    return [spec[0] for spec in specializations]


@router.get("/{doctor_id}", response_model=schemas.Doctor)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Get a specific doctor by ID"""
    doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@router.put("/{doctor_id}", response_model=schemas.Doctor)
def update_doctor(doctor_id: int, doctor_update: schemas.DoctorUpdate, db: Session = Depends(get_db)):
    """Update doctor information"""
    db_doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == doctor_id).first()
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    update_data = doctor_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_doctor, key, value)
    
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Delete a doctor"""
    db_doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == doctor_id).first()
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    db.delete(db_doctor)
    db.commit()
    return None

@router.get("/{doctor_id}/appointments", response_model=List[schemas.Appointment])
def get_doctor_appointments(doctor_id: int, db: Session = Depends(get_db)):
    """Get all appointments for a specific doctor"""
    doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return doctor.appointments