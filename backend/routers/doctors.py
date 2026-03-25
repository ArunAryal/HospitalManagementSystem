from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.database import get_db
from backend import models, schemas

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/", response_model=list[schemas.Doctor])
def list_doctors(
    specialization: Optional[str] = Query(None),
    available_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(models.Doctor)
    if specialization:
        query = query.filter(models.Doctor.specialization.ilike(f"%{specialization}%"))
    if available_only:
        query = query.filter(models.Doctor.is_available == True)
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=schemas.Doctor, status_code=201)
def create_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Doctor).filter(models.Doctor.email == doctor.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Doctor with this email already exists")
    db_doctor = models.Doctor(**doctor.model_dump())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


@router.get("/{doctor_id}", response_model=schemas.Doctor)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.put("/{doctor_id}", response_model=schemas.Doctor)
def update_doctor(doctor_id: int, update: schemas.DoctorUpdate, db: Session = Depends(get_db)):
    doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(doctor, field, value)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.delete("/{doctor_id}", status_code=204)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(doctor)
    db.commit()