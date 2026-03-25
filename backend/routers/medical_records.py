from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from typing import Optional
from ..database import get_db
from .. import models
from .. import schemas

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])


@router.get("/", response_model=list[schemas.MedicalRecord])
def list_medical_records(
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(models.MedicalRecord).options(
        selectinload(models.MedicalRecord.patient),
        selectinload(models.MedicalRecord.doctor)
    )
    if patient_id:
        query = query.filter(models.MedicalRecord.patient_id == patient_id)
    if doctor_id:
        query = query.filter(models.MedicalRecord.doctor_id == doctor_id)
    return (
        query.order_by(models.MedicalRecord.record_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/", response_model=schemas.MedicalRecord, status_code=201)
def create_medical_record(
    record: schemas.MedicalRecordCreate, db: Session = Depends(get_db)
):
    if (
        not db.query(models.Patient)
        .filter(models.Patient.patient_id == record.patient_id)
        .first()
    ):
        raise HTTPException(status_code=404, detail="Patient not found")
    if (
        not db.query(models.Doctor)
        .filter(models.Doctor.doctor_id == record.doctor_id)
        .first()
    ):
        raise HTTPException(status_code=404, detail="Doctor not found")
    if record.appointment_id:
        if (
            not db.query(models.Appointment)
            .filter(models.Appointment.appointment_id == record.appointment_id)
            .first()
        ):
            raise HTTPException(status_code=404, detail="Appointment not found")

    db_record = models.MedicalRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.get("/{record_id}", response_model=schemas.MedicalRecord)
def get_medical_record(record_id: int, db: Session = Depends(get_db)):
    record = (
        db.query(models.MedicalRecord)
        .filter(models.MedicalRecord.record_id == record_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    return record


@router.put("/{record_id}", response_model=schemas.MedicalRecord)
def update_medical_record(
    record_id: int, update: schemas.MedicalRecordUpdate, db: Session = Depends(get_db)
):
    record = (
        db.query(models.MedicalRecord)
        .filter(models.MedicalRecord.record_id == record_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=204)
def delete_medical_record(record_id: int, db: Session = Depends(get_db)):
    record = (
        db.query(models.MedicalRecord)
        .filter(models.MedicalRecord.record_id == record_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    db.delete(record)
    db.commit()


# ── Prescriptions (nested under a record) ──────────────────────────────────────


@router.get("/{record_id}/prescriptions", response_model=list[schemas.Prescription])
def list_prescriptions(record_id: int, db: Session = Depends(get_db)):
    if (
        not db.query(models.MedicalRecord)
        .filter(models.MedicalRecord.record_id == record_id)
        .first()
    ):
        raise HTTPException(status_code=404, detail="Medical record not found")
    return (
        db.query(models.Prescription)
        .filter(models.Prescription.medical_record_id == record_id)
        .all()
    )


@router.post(
    "/{record_id}/prescriptions", response_model=schemas.Prescription, status_code=201
)
def add_prescription(
    record_id: int,
    prescription: schemas.PrescriptionCreate,
    db: Session = Depends(get_db),
):
    if prescription.medical_record_id != record_id:
        raise HTTPException(
            status_code=400, detail="medical_record_id in body must match URL"
        )
    if (
        not db.query(models.MedicalRecord)
        .filter(models.MedicalRecord.record_id == record_id)
        .first()
    ):
        raise HTTPException(status_code=404, detail="Medical record not found")

    medicine = (
        db.query(models.Medicine)
        .filter(models.Medicine.medicine_id == prescription.medicine_id)
        .first()
    )
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    if medicine.stock_quantity < prescription.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Available: {medicine.stock_quantity}",
        )

    # Note: Stock deduction is handled by database trigger after_prescription_insert
    db_prescription = models.Prescription(**prescription.model_dump())
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription


@router.delete("/prescriptions/{prescription_id}", status_code=204)
def delete_prescription(prescription_id: int, db: Session = Depends(get_db)):
    presc = (
        db.query(models.Prescription)
        .filter(models.Prescription.prescription_id == prescription_id)
        .first()
    )
    if not presc:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Note: Stock restoration should be handled by database trigger
    # (if a delete trigger is added to the database schema)
    db.delete(presc)
    db.commit()
