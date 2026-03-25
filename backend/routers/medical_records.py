from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import schemas
from backend.services import MedicalRecordService, MedicalRecordRepository
from backend.exceptions import APIException

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])


def get_medical_record_service(
    db: Session = Depends(get_db),
) -> MedicalRecordService:
    """Dependency injection for MedicalRecordService."""
    return MedicalRecordService(MedicalRecordRepository(db), db)


@router.get("/", response_model=List[schemas.MedicalRecord])
def list_medical_records(
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: MedicalRecordService = Depends(get_medical_record_service),
):
    """List all medical records."""
    try:
        if patient_id:
            return service.get_patient_medical_records(
                patient_id, skip=skip, limit=limit
            )
        if doctor_id:
            return service.get_doctor_medical_records(doctor_id, skip=skip, limit=limit)
        return service.list_medical_records(skip=skip, limit=limit)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/", response_model=schemas.MedicalRecord, status_code=201)
def create_medical_record(
    record: schemas.MedicalRecordCreate,
    service: MedicalRecordService = Depends(get_medical_record_service),
):
    """Create a new medical record."""
    try:
        return service.create_medical_record(record)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{record_id}", response_model=schemas.MedicalRecord)
def get_medical_record(
    record_id: int,
    service: MedicalRecordService = Depends(get_medical_record_service),
):
    """Get a single medical record."""
    try:
        return service.get_medical_record(record_id)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{record_id}", response_model=schemas.MedicalRecord)
def update_medical_record(
    record_id: int,
    update: schemas.MedicalRecordUpdate,
    service: MedicalRecordService = Depends(get_medical_record_service),
):
    """Update a medical record."""
    try:
        return service.update_medical_record(record_id, update)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{record_id}", status_code=204)
def delete_medical_record(
    record_id: int,
    service: MedicalRecordService = Depends(get_medical_record_service),
):
    """Delete a medical record."""
    try:
        service.delete_medical_record(record_id)
        return None
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{record_id}/prescriptions", response_model=List[schemas.Prescription])
def list_prescriptions(record_id: int, db: Session = Depends(get_db)):
    """Get prescriptions for a medical record."""
    from backend import models

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
    """Add a prescription to a medical record."""
    from backend import models
    from backend.services import MedicineService, MedicineRepository

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

    medicine_service = MedicineService(MedicineRepository(db))
    medicine = medicine_service.get_medicine(prescription.medicine_id)

    # Check stock
    if medicine.stock_quantity < prescription.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Available: {medicine.stock_quantity}",
        )

    db_prescription = models.Prescription(**prescription.model_dump())
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)

    return db_prescription


@router.delete("/prescriptions/{prescription_id}", status_code=204)
def delete_prescription(prescription_id: int, db: Session = Depends(get_db)):
    """Delete a prescription."""
    from backend import models

    presc = (
        db.query(models.Prescription)
        .filter(models.Prescription.prescription_id == prescription_id)
        .first()
    )
    if not presc:
        raise HTTPException(status_code=404, detail="Prescription not found")

    db.delete(presc)
    db.commit()
