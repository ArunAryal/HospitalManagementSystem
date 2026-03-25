from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from typing import Optional
from ..database import get_db
from .. import models
from .. import schemas

router = APIRouter(prefix="/bills", tags=["Billing"])


@router.get("/", response_model=list[schemas.Bill])
def list_bills(
    patient_id: Optional[int] = None,
    payment_status: Optional[str] = Query(
        None, pattern="^(Pending|Paid|Partially Paid)$"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(models.Bill).options(
        selectinload(models.Bill.patient)
    )
    if patient_id:
        query = query.filter(models.Bill.patient_id == patient_id)
    if payment_status:
        query = query.filter(
            models.Bill.payment_status == models.PaymentStatus(payment_status)
        )
    return query.order_by(models.Bill.bill_date.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=schemas.Bill, status_code=201)
def create_bill(bill: schemas.BillCreate, db: Session = Depends(get_db)):
    if not db.query(models.Patient).filter(models.Patient.patient_id == bill.patient_id).first():
        raise HTTPException(status_code=404, detail="Patient not found")
    if bill.admission_id:
        if not db.query(models.Admission).filter(
            models.Admission.admission_id == bill.admission_id
        ).first():
            raise HTTPException(status_code=404, detail="Admission not found")
    if bill.appointment_id:
        if not db.query(models.Appointment).filter(
            models.Appointment.appointment_id == bill.appointment_id
        ).first():
            raise HTTPException(status_code=404, detail="Appointment not found")

    db_bill = models.Bill(**bill.model_dump())
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill


@router.get("/{bill_id}", response_model=schemas.Bill)
def get_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(models.Bill).filter(models.Bill.bill_id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill


@router.put("/{bill_id}", response_model=schemas.Bill)
def update_bill(bill_id: int, update: schemas.BillUpdate, db: Session = Depends(get_db)):
    bill = db.query(models.Bill).filter(models.Bill.bill_id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    data = update.model_dump(exclude_unset=True)

    if "payment_status" in data:
        bill.payment_status = models.PaymentStatus(data.pop("payment_status"))

    if "payment_method" in data:
        bill.payment_method = models.PaymentMethod(data.pop("payment_method"))

    for field, value in data.items():
        setattr(bill, field, value)

    db.commit()
    db.refresh(bill)
    return bill


@router.delete("/{bill_id}", status_code=204)
def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(models.Bill).filter(models.Bill.bill_id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    db.delete(bill)
    db.commit()


@router.post("/admission/{admission_id}/generate", response_model=schemas.Bill, status_code=201)
def generate_bill_for_admission(admission_id: int, db: Session = Depends(get_db)):
    """Generate or get auto-calculated bill for an admission."""
    # Check if admission exists
    admission = db.query(models.Admission).filter(
        models.Admission.admission_id == admission_id
    ).first()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")
    
    # Check if bill already exists
    existing_bill = db.query(models.Bill).filter(
        models.Bill.admission_id == admission_id
    ).first()
    if existing_bill:
        return existing_bill
    
    # Get room daily rate
    room = db.query(models.Room).filter(models.Room.room_id == admission.room_id).first()
    room_charges = room.charge_per_day if room else 0
    
    # Create new bill
    db_bill = models.Bill(
        patient_id=admission.patient_id,
        admission_id=admission_id,
        consultation_fee=0,
        medicine_charges=0,
        room_charges=room_charges,
        other_charges=0,
        total_amount=room_charges,
    )
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill