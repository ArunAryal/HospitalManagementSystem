from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import schemas
from backend.services import DoctorService, DoctorRepository
from backend.exceptions import APIException

router = APIRouter(prefix="/doctors", tags=["Doctors"])


def get_doctor_service(db: Session = Depends(get_db)) -> DoctorService:
    """Dependency injection for DoctorService."""
    return DoctorService(DoctorRepository(db))


@router.get("/", response_model=List[schemas.Doctor])
def list_doctors(
    specialization: str = Query(None),
    available_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: DoctorService = Depends(get_doctor_service),
):
    """List all doctors with optional filters."""
    try:
        if specialization:
            return service.list_doctors_by_specialization(
                specialization, skip=skip, limit=limit
            )
        if available_only:
            return service.list_available_doctors(skip=skip, limit=limit)
        return service.list_doctors(skip=skip, limit=limit)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/", response_model=schemas.Doctor, status_code=201)
def create_doctor(
    doctor: schemas.DoctorCreate,
    service: DoctorService = Depends(get_doctor_service),
):
    """Create a new doctor."""
    try:
        return service.create_doctor(doctor)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{doctor_id}", response_model=schemas.Doctor)
def get_doctor(
    doctor_id: int,
    service: DoctorService = Depends(get_doctor_service),
):
    """Get a single doctor."""
    try:
        return service.get_doctor(doctor_id)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{doctor_id}", response_model=schemas.Doctor)
def update_doctor(
    doctor_id: int,
    update: schemas.DoctorUpdate,
    service: DoctorService = Depends(get_doctor_service),
):
    """Update a doctor."""
    try:
        return service.update_doctor(doctor_id, update)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{doctor_id}", status_code=204)
def delete_doctor(
    doctor_id: int,
    service: DoctorService = Depends(get_doctor_service),
):
    """Delete a doctor."""
    try:
        service.delete_doctor(doctor_id)
        return None
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{doctor_id}/availability")
def set_doctor_availability(
    doctor_id: int,
    is_available: bool,
    service: DoctorService = Depends(get_doctor_service),
):
    """Set doctor availability."""
    try:
        return service.set_doctor_availability(doctor_id, is_available)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
