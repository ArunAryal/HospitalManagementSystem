from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from backend.database import get_db
from backend import models, schemas

router = APIRouter(tags=["Rooms & Admissions"])


# ── Rooms ──────────────────────────────────────────────────────────────────────

@router.get("/rooms", response_model=list[schemas.Room])
def list_rooms(
    room_type: Optional[str] = Query(None, pattern="^(General|Private|ICU|Emergency)$"),
    available_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    query = db.query(models.Room)
    if room_type:
        query = query.filter(models.Room.room_type == models.RoomType(room_type))
    if available_only:
        query = query.filter(models.Room.is_available == True)
    return query.order_by(models.Room.room_number).all()


@router.post("/rooms", response_model=schemas.Room, status_code=201)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Room).filter(models.Room.room_number == room.room_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Room number already exists")
    db_room = models.Room(**room.model_dump())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@router.get("/rooms/{room_id}", response_model=schemas.Room)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.put("/rooms/{room_id}", response_model=schemas.Room)
def update_room(room_id: int, update: schemas.RoomUpdate, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(room, field, value)
    db.commit()
    db.refresh(room)
    return room


@router.delete("/rooms/{room_id}", status_code=204)
def delete_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.current_occupancy > 0:
        raise HTTPException(status_code=400, detail="Cannot delete a room with active admissions")
    db.delete(room)
    db.commit()


# ── Admissions ─────────────────────────────────────────────────────────────────

@router.get("/admissions", response_model=list[schemas.Admission])
def list_admissions(
    patient_id: Optional[int] = None,
    status: Optional[str] = Query(None, pattern="^(Active|Discharged)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(models.Admission)
    if patient_id:
        query = query.filter(models.Admission.patient_id == patient_id)
    if status:
        query = query.filter(models.Admission.status == status)
    return query.order_by(models.Admission.admission_date.desc()).offset(skip).limit(limit).all()


@router.post("/admissions", response_model=schemas.Admission, status_code=201)
def admit_patient(admission: schemas.AdmissionCreate, db: Session = Depends(get_db)):
    if not db.query(models.Patient).filter(models.Patient.patient_id == admission.patient_id).first():
        raise HTTPException(status_code=404, detail="Patient not found")
    if not db.query(models.Doctor).filter(models.Doctor.doctor_id == admission.doctor_id).first():
        raise HTTPException(status_code=404, detail="Doctor not found")

    room = db.query(models.Room).filter(models.Room.room_id == admission.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not room.is_available:
        raise HTTPException(status_code=400, detail="Room is not available")
    if room.current_occupancy >= room.capacity:
        raise HTTPException(status_code=400, detail="Room is at full capacity")

    # Update room occupancy
    room.current_occupancy += 1
    if room.current_occupancy >= room.capacity:
        room.is_available = False

    db_admission = models.Admission(**admission.model_dump())
    db.add(db_admission)
    db.commit()
    db.refresh(db_admission)
    return db_admission


@router.get("/admissions/{admission_id}", response_model=schemas.Admission)
def get_admission(admission_id: int, db: Session = Depends(get_db)):
    admission = db.query(models.Admission).filter(
        models.Admission.admission_id == admission_id
    ).first()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")
    return admission


@router.put("/admissions/{admission_id}", response_model=schemas.Admission)
def update_admission(
    admission_id: int, update: schemas.AdmissionUpdate, db: Session = Depends(get_db)
):
    admission = db.query(models.Admission).filter(
        models.Admission.admission_id == admission_id
    ).first()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")

    data = update.model_dump(exclude_unset=True)

    # Handle discharge: free up the room
    if data.get("status") == "Discharged" and admission.status == "Active":
        if not data.get("discharge_date"):
            data["discharge_date"] = datetime.utcnow()

        room = db.query(models.Room).filter(models.Room.room_id == admission.room_id).first()
        if room:
            room.current_occupancy = max(0, room.current_occupancy - 1)
            room.is_available = True

    for field, value in data.items():
        setattr(admission, field, value)

    db.commit()
    db.refresh(admission)
    return admission