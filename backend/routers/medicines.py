from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend import models, schemas

router = APIRouter(
    prefix="/medicines",
    tags=["Medicines"]
)


# ── Medicines ──────────────────────────────────────────────────────────────────

@router.post("/", response_model=schemas.Medicine, status_code=status.HTTP_201_CREATED)
def create_medicine(medicine: schemas.MedicineCreate, db: Session = Depends(get_db)):
    """Add a new medicine to inventory"""
    existing = db.query(models.Medicine).filter(
        models.Medicine.medicine_name == medicine.medicine_name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Medicine with this name already exists")

    db_medicine = models.Medicine(**medicine.dict())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine


@router.get("/", response_model=List[schemas.Medicine])
def get_medicines(
    skip: int = 0,
    limit: int = 100,
    low_stock_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all medicines; use low_stock_only=true to see items at or below reorder level"""
    query = db.query(models.Medicine)
    if low_stock_only:
        query = query.filter(models.Medicine.stock_quantity <= models.Medicine.reorder_level)
    return query.offset(skip).limit(limit).all()


@router.get("/{medicine_id}", response_model=schemas.Medicine)
def get_medicine(medicine_id: int, db: Session = Depends(get_db)):
    """Get a specific medicine by ID"""
    medicine = db.query(models.Medicine).filter(
        models.Medicine.medicine_id == medicine_id
    ).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return medicine


@router.put("/{medicine_id}", response_model=schemas.Medicine)
def update_medicine(
    medicine_id: int,
    medicine_update: schemas.MedicineUpdate,
    db: Session = Depends(get_db)
):
    """Update medicine price, stock quantity, or reorder level"""
    db_medicine = db.query(models.Medicine).filter(
        models.Medicine.medicine_id == medicine_id
    ).first()
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    update_data = medicine_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_medicine, key, value)

    db.commit()
    db.refresh(db_medicine)
    return db_medicine


@router.delete("/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medicine(medicine_id: int, db: Session = Depends(get_db)):
    """Delete a medicine from inventory"""
    db_medicine = db.query(models.Medicine).filter(
        models.Medicine.medicine_id == medicine_id
    ).first()
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    db.delete(db_medicine)
    db.commit()
    return None


# ── Prescriptions ──────────────────────────────────────────────────────────────

@router.post("/prescriptions", response_model=schemas.Prescription, status_code=status.HTTP_201_CREATED)
def create_prescription(prescription: schemas.PrescriptionCreate, db: Session = Depends(get_db)):
    """Add a prescription to a medical record"""
    # Verify medical record exists
    record = db.query(models.MedicalRecord).filter(
        models.MedicalRecord.record_id == prescription.medical_record_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")

    # Verify medicine exists and has sufficient stock
    medicine = db.query(models.Medicine).filter(
        models.Medicine.medicine_id == prescription.medicine_id
    ).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    if medicine.stock_quantity < prescription.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Available: {medicine.stock_quantity}, Requested: {prescription.quantity}"
        )

    db_prescription = models.Prescription(**prescription.dict())
    db.add(db_prescription)



    db.commit()
    db.refresh(db_prescription)
    return db_prescription


@router.get("/prescriptions", response_model=List[schemas.Prescription])
def get_prescriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all prescriptions"""
    return db.query(models.Prescription).offset(skip).limit(limit).all()


@router.get("/prescriptions/{prescription_id}", response_model=schemas.Prescription)
def get_prescription(prescription_id: int, db: Session = Depends(get_db)):
    """Get a specific prescription by ID"""
    prescription = db.query(models.Prescription).filter(
        models.Prescription.prescription_id == prescription_id
    ).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription


@router.get("/medical-records/{record_id}/prescriptions", response_model=List[schemas.Prescription])
def get_prescriptions_by_record(record_id: int, db: Session = Depends(get_db)):
    """Get all prescriptions for a specific medical record"""
    record = db.query(models.MedicalRecord).filter(
        models.MedicalRecord.record_id == record_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    return record.prescriptions


@router.delete("/prescriptions/{prescription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prescription(prescription_id: int, db: Session = Depends(get_db)):
    """Delete a prescription and restore stock"""
    db_prescription = db.query(models.Prescription).filter(
        models.Prescription.prescription_id == prescription_id
    ).first()
    if not db_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Restore stock on deletion
    medicine = db.query(models.Medicine).filter(
        models.Medicine.medicine_id == db_prescription.medicine_id
    ).first()
    if medicine:
        medicine.stock_quantity += db_prescription.quantity

    db.delete(db_prescription)
    db.commit()
    return None