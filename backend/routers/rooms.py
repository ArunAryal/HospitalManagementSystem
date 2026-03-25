from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import schemas
from backend.services import (
    RoomService,
    RoomRepository,
    AdmissionService,
    AdmissionRepository,
)
from backend.exceptions import APIException

router = APIRouter(prefix="", tags=["Rooms & Admissions"])


def get_room_service(db: Session = Depends(get_db)) -> RoomService:
    """Dependency injection for RoomService."""
    return RoomService(RoomRepository(db), db)


def get_admission_service(db: Session = Depends(get_db)) -> AdmissionService:
    """Dependency injection for AdmissionService."""
    return AdmissionService(AdmissionRepository(db), RoomRepository(db), db)


# ── Rooms ──────────────────────────────────────────────────────────────────────


@router.get("/rooms", response_model=List[schemas.Room])
def list_rooms(
    room_type: Optional[str] = Query(None, pattern="^(General|Private|ICU|Emergency)$"),
    available_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: RoomService = Depends(get_room_service),
):
    """List all rooms."""
    try:
        if room_type:
            return service.list_rooms_by_type(room_type, skip=skip, limit=limit)
        if available_only:
            return service.list_available_rooms(skip=skip, limit=limit)
        return service.list_rooms(skip=skip, limit=limit)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/rooms", response_model=schemas.Room, status_code=201)
def create_room(
    room: schemas.RoomCreate,
    service: RoomService = Depends(get_room_service),
):
    """Create a new room."""
    try:
        return service.create_room(room)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/rooms/{room_id}", response_model=schemas.Room)
def get_room(
    room_id: int,
    service: RoomService = Depends(get_room_service),
):
    """Get a single room."""
    try:
        return service.get_room(room_id)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/rooms/{room_id}", response_model=schemas.Room)
def update_room(
    room_id: int,
    update: schemas.RoomUpdate,
    service: RoomService = Depends(get_room_service),
):
    """Update a room."""
    try:
        return service.update_room(room_id, update)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/rooms/{room_id}", status_code=204)
def delete_room(
    room_id: int,
    service: RoomService = Depends(get_room_service),
):
    """Delete a room."""
    try:
        service.delete_room(room_id)
        return None
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/rooms/stats/occupancy", response_model=dict)
def get_occupancy_stats(
    service: RoomService = Depends(get_room_service),
):
    """Get room occupancy statistics."""
    try:
        return service.get_room_occupancy_stats()
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# ── Admissions ─────────────────────────────────────────────────────────────────


@router.get("/admissions", response_model=List[schemas.Admission])
def list_admissions(
    patient_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: AdmissionService = Depends(get_admission_service),
):
    """List all admissions."""
    try:
        if patient_id:
            return service.get_patient_admissions(patient_id, skip=skip, limit=limit)
        return service.list_admissions(skip=skip, limit=limit)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/admissions", response_model=schemas.Admission, status_code=201)
def admit_patient(
    admission: schemas.AdmissionCreate,
    service: AdmissionService = Depends(get_admission_service),
):
    """Admit a patient to a room."""
    try:
        return service.admit_patient(admission)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/admissions/{admission_id}", response_model=schemas.Admission)
def get_admission(
    admission_id: int,
    service: AdmissionService = Depends(get_admission_service),
):
    """Get a single admission."""
    try:
        return service.get_admission(admission_id)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/admissions/{admission_id}", response_model=schemas.Admission)
def update_admission(
    admission_id: int,
    update: schemas.AdmissionUpdate,
    service: AdmissionService = Depends(get_admission_service),
):
    """Update an admission record."""
    try:
        return service.update_admission(admission_id, update)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/admissions/{admission_id}/discharge", response_model=schemas.Admission)
def discharge_patient(
    admission_id: int,
    update: schemas.AdmissionUpdate,
    service: AdmissionService = Depends(get_admission_service),
):
    """Discharge a patient from admission."""
    try:
        return service.discharge_patient(admission_id)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/admissions/active", response_model=List[schemas.Admission])
def get_active_admissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: AdmissionService = Depends(get_admission_service),
):
    """Get currently active admissions."""
    try:
        return service.get_active_admissions(skip=skip, limit=limit)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/admissions/{admission_id}", status_code=204)
def delete_admission(
    admission_id: int,
    service: AdmissionService = Depends(get_admission_service),
):
    """Delete an admission record."""
    try:
        service.delete_admission(admission_id)
        return None
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/admissions/stats", response_model=dict)
def get_admission_stats(
    service: AdmissionService = Depends(get_admission_service),
):
    """Get admission statistics."""
    try:
        return service.get_admission_statistics()
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
