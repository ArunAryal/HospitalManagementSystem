from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend import models, schemas

router = APIRouter(
    prefix="/billing",
    tags=["Billing"]
)


# ── Rooms ──────────────────────────────────────────────────────────────────────

@router.post("/rooms", response_model=schemas.Room, status_code=status.HTTP_201_CREATED)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    """Add a new room"""
    existing = db.query(models.Room).filter(models.Room.room_number == room.room_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Room number already exists")

    db_room = models.Room(**room.dict())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@router.get("/rooms", response_model=List[schemas.Room])
def get_rooms(available_only: bool = False, db: Session = Depends(get_db)):
    """Get all rooms, optionally filter to available ones only"""
    query = db.query(models.Room)
    if available_only:
        query = query.filter(models.Room.is_available == True)
    return query.all()


@router.get("/rooms/{room_id}", response_model=schemas.Room)
def get_room(room_id: int, db: Session = Depends(get_db)):
    """Get a specific room by ID"""
    room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.put("/rooms/{room_id}", response_model=schemas.Room)
def update_room(room_id: int, room_update: schemas.RoomUpdate, db: Session = Depends(get_db)):
    """Update room details"""
    db_room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")

    update_data = room_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_room, key, value)

    db.commit()
    db.refresh(db_room)
    return db_room


# ── Admissions ─────────────────────────────────────────────────────────────────

@router.post("/admissions", response_model=schemas.Admission, status_code=status.HTTP_201_CREATED)
def create_admission(admission: schemas.AdmissionCreate, db: Session = Depends(get_db)):
    """Admit a patient to a room"""
    # Verify patient
    patient = db.query(models.Patient).filter(models.Patient.patient_id == admission.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Verify doctor
    doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == admission.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Verify room exists and has capacity
    room = db.query(models.Room).filter(models.Room.room_id == admission.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not room.is_available:
        raise HTTPException(status_code=400, detail="Room is not available")
    if room.current_occupancy >= room.capacity:
        raise HTTPException(status_code=400, detail="Room is at full capacity")

    # Check patient doesn't already have an active admission
    active = db.query(models.Admission).filter(
        models.Admission.patient_id == admission.patient_id,
        models.Admission.status == "Active"
    ).first()
    if active:
        raise HTTPException(status_code=400, detail="Patient already has an active admission")

    db_admission = models.Admission(**admission.dict())
    db.add(db_admission)


    db.commit()
    db.refresh(db_admission)
    return db_admission


@router.get("/admissions", response_model=List[schemas.Admission])
def get_admissions(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all admissions"""
    query = db.query(models.Admission)
    if active_only:
        query = query.filter(models.Admission.status == "Active")
    return query.offset(skip).limit(limit).all()


@router.get("/admissions/{admission_id}", response_model=schemas.Admission)
def get_admission(admission_id: int, db: Session = Depends(get_db)):
    """Get a specific admission by ID"""
    admission = db.query(models.Admission).filter(
        models.Admission.admission_id == admission_id
    ).first()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")
    return admission


@router.put("/admissions/{admission_id}", response_model=schemas.Admission)
def update_admission(
    admission_id: int,
    admission_update: schemas.AdmissionUpdate,
    db: Session = Depends(get_db)
):
    """Discharge a patient or update admission details"""
    db_admission = db.query(models.Admission).filter(
        models.Admission.admission_id == admission_id
    ).first()
    if not db_admission:
        raise HTTPException(status_code=404, detail="Admission not found")


    update_data = admission_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_admission, key, value)

    db.commit()
    db.refresh(db_admission)
    return db_admission


# ── Bills ──────────────────────────────────────────────────────────────────────

@router.post("/bills", response_model=schemas.Bill, status_code=status.HTTP_201_CREATED)
def create_bill(bill: schemas.BillCreate, db: Session = Depends(get_db)):
    """Create a new bill for a patient"""
    # Verify patient
    patient = db.query(models.Patient).filter(models.Patient.patient_id == bill.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Verify admission if provided
    if bill.admission_id:
        admission = db.query(models.Admission).filter(
            models.Admission.admission_id == bill.admission_id
        ).first()
        if not admission:
            raise HTTPException(status_code=404, detail="Admission not found")

    # Verify appointment if provided
    if bill.appointment_id:
        appointment = db.query(models.Appointment).filter(
            models.Appointment.appointment_id == bill.appointment_id
        ).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

    db_bill = models.Bill(**bill.dict())
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill


@router.get("/bills", response_model=List[schemas.Bill])
def get_bills(
    skip: int = 0,
    limit: int = 100,
    payment_status: str = None,
    db: Session = Depends(get_db)
):
    """Get all bills, optionally filter by payment status"""
    query = db.query(models.Bill)
    if payment_status:
        query = query.filter(models.Bill.payment_status == payment_status)
    return query.offset(skip).limit(limit).all()


@router.get("/bills/{bill_id}", response_model=schemas.Bill)
def get_bill(bill_id: int, db: Session = Depends(get_db)):
    """Get a specific bill by ID"""
    bill = db.query(models.Bill).filter(models.Bill.bill_id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill


@router.get("/patients/{patient_id}/bills", response_model=List[schemas.Bill])
def get_patient_bills(patient_id: int, db: Session = Depends(get_db)):
    """Get all bills for a specific patient"""
    patient = db.query(models.Patient).filter(models.Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient.bills


@router.put("/bills/{bill_id}", response_model=schemas.Bill)
def update_bill(bill_id: int, bill_update: schemas.BillUpdate, db: Session = Depends(get_db)):
    """Update payment status or method for a bill"""
    db_bill = db.query(models.Bill).filter(models.Bill.bill_id == bill_id).first()
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    update_data = bill_update.dict(exclude_unset=True)

    # Validate paid_amount doesn't exceed total
    new_paid = update_data.get("paid_amount", float(db_bill.paid_amount))
    if new_paid > float(db_bill.total_amount):
        raise HTTPException(
            status_code=400,
            detail=f"Paid amount ({new_paid}) cannot exceed total amount ({db_bill.total_amount})"
        )

    for key, value in update_data.items():
        setattr(db_bill, key, value)

    db.commit()
    db.refresh(db_bill)
    return db_bill


@router.delete("/bills/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    """Delete a bill"""
    db_bill = db.query(models.Bill).filter(models.Bill.bill_id == bill_id).first()
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    db.delete(db_bill)
    db.commit()
    return None