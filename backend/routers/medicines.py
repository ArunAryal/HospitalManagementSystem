from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.database import get_db
from backend import models, schemas

router = APIRouter(prefix="/medicines", tags=["Medicines"])


@router.get("/", response_model=list[schemas.Medicine])
def list_medicines(
    search: Optional[str] = Query(None, description="Search by name or manufacturer"),
    low_stock: bool = Query(False, description="Filter medicines at or below reorder level"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(models.Medicine)
    if search:
        like = f"%{search}%"
        query = query.filter(
            models.Medicine.medicine_name.ilike(like)
            | models.Medicine.manufacturer.ilike(like)
        )
    if low_stock:
        query = query.filter(
            models.Medicine.stock_quantity <= models.Medicine.reorder_level
        )
    return query.order_by(models.Medicine.medicine_name).offset(skip).limit(limit).all()


@router.post("/", response_model=schemas.Medicine, status_code=201)
def create_medicine(medicine: schemas.MedicineCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Medicine).filter(
        models.Medicine.medicine_name == medicine.medicine_name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Medicine with this name already exists")
    db_medicine = models.Medicine(**medicine.model_dump())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine


@router.get("/low-stock", response_model=list[schemas.Medicine])
def get_low_stock_medicines(db: Session = Depends(get_db)):
    """Returns all medicines at or below their reorder level."""
    return (
        db.query(models.Medicine)
        .filter(models.Medicine.stock_quantity <= models.Medicine.reorder_level)
        .order_by(models.Medicine.stock_quantity)
        .all()
    )


@router.get("/{medicine_id}", response_model=schemas.Medicine)
def get_medicine(medicine_id: int, db: Session = Depends(get_db)):
    medicine = db.query(models.Medicine).filter(models.Medicine.medicine_id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return medicine


@router.put("/{medicine_id}", response_model=schemas.Medicine)
def update_medicine(
    medicine_id: int, update: schemas.MedicineUpdate, db: Session = Depends(get_db)
):
    medicine = db.query(models.Medicine).filter(models.Medicine.medicine_id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(medicine, field, value)
    db.commit()
    db.refresh(medicine)
    return medicine


@router.patch("/{medicine_id}/restock", response_model=schemas.Medicine)
def restock_medicine(
    medicine_id: int,
    quantity: int = Query(..., gt=0, description="Units to add to stock"),
    db: Session = Depends(get_db),
):
    medicine = db.query(models.Medicine).filter(models.Medicine.medicine_id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    medicine.stock_quantity += quantity
    db.commit()
    db.refresh(medicine)
    return medicine


@router.delete("/{medicine_id}", status_code=204)
def delete_medicine(medicine_id: int, db: Session = Depends(get_db)):
    medicine = db.query(models.Medicine).filter(models.Medicine.medicine_id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    db.delete(medicine)
    db.commit()