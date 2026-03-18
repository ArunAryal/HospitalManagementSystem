from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend import models, schemas

router = APIRouter(
    prefix="/medical-records",
    tags=["Medical Records"]
)

@router.post("/", response_model=schemas.MedicalRecord, status_code=status.HTTP_201_CREATED)
def create_medical_record(record: schemas.MedicalRecordCreate, db: Session = Depends(get_db)):
    """Create a new medical record"""
    # Verify patient exists
    patient = db.query(models.Patient).filter(models.Patient.patient_id == record.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Verify doctor exists
    doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == record.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Verify appointment exists if provided
    if record.appointment_id:
        appointment = db.query(models.Appointment).filter(
            models.Appointment.appointment_id == record.appointment_id
        ).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
    
    db_record = models.MedicalRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.get("/", response_model=List[schemas.MedicalRecord])
def get_medical_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all medical records"""
    records = db.query(models.MedicalRecord).offset(skip).limit(limit).all()
    return records

@router.get("/{record_id}", response_model=schemas.MedicalRecord)
def get_medical_record(record_id: int, db: Session = Depends(get_db)):
    """Get a specific medical record by ID"""
    record = db.query(models.MedicalRecord).filter(
        models.MedicalRecord.record_id == record_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    return record

@router.put("/{record_id}", response_model=schemas.MedicalRecord)
def update_medical_record(record_id: int, record_update: schemas.MedicalRecordUpdate, db: Session = Depends(get_db)):
    """Update a medical record"""
    db_record = db.query(models.MedicalRecord).filter(
        models.MedicalRecord.record_id == record_id
    ).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    
    update_data = record_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    db.commit()
    db.refresh(db_record)
    return db_record

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medical_record(record_id: int, db: Session = Depends(get_db)):
    """Delete a medical record"""
    db_record = db.query(models.MedicalRecord).filter(
        models.MedicalRecord.record_id == record_id
    ).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    
    db.delete(db_record)
    db.commit()
    return None
