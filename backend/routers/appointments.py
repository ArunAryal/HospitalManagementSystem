from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import schemas
from backend.services import AppointmentService, AppointmentRepository
from backend.exceptions import APIException

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def get_appointment_service(db: Session = Depends(get_db)) -> AppointmentService:
    """Dependency injection for AppointmentService."""
    return AppointmentService(AppointmentRepository(db), db)


@router.get("/", response_model=List[schemas.Appointment])
def list_appointments(
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    appointment_date: Optional[date] = None,
    status: Optional[str] = Query(
        None, pattern="^(Scheduled|Completed|Cancelled|No-Show)$"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: AppointmentService = Depends(get_appointment_service),
):
    """List all appointments with optional filters."""
    try:
        return service.list_appointments(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            status=status,
            skip=skip,
            limit=limit,
        )
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/", response_model=schemas.Appointment, status_code=201)
def create_appointment(
    appt: schemas.AppointmentCreate,
    service: AppointmentService = Depends(get_appointment_service),
):
    """Create a new appointment."""
    try:
        return service.create_appointment(appt)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/{appointment_id}", response_model=schemas.Appointment)
def get_appointment(
    appointment_id: int,
    service: AppointmentService = Depends(get_appointment_service),
):
    """Get a single appointment."""
    try:
        return service.get_appointment(appointment_id)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put("/{appointment_id}", response_model=schemas.Appointment)
def update_appointment(
    appointment_id: int,
    update: schemas.AppointmentUpdate,
    service: AppointmentService = Depends(get_appointment_service),
):
    """Update an appointment."""
    try:
        return service.update_appointment(appointment_id, update)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: int,
    service: AppointmentService = Depends(get_appointment_service),
):
    """Cancel an appointment."""
    try:
        return service.cancel_appointment(appointment_id)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/patient/{patient_id}", response_model=List[schemas.Appointment])
def get_patient_appointments(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: AppointmentService = Depends(get_appointment_service),
):
    """Get all appointments for a patient."""
    try:
        return service.get_patient_appointments(patient_id, skip=skip, limit=limit)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/doctor/{doctor_id}", response_model=List[schemas.Appointment])
def get_doctor_appointments(
    doctor_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: AppointmentService = Depends(get_appointment_service),
):
    """Get all appointments for a doctor."""
    try:
        return service.get_doctor_appointments(doctor_id, skip=skip, limit=limit)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete("/{appointment_id}", status_code=204)
def delete_appointment(
    appointment_id: int,
    service: AppointmentService = Depends(get_appointment_service),
):
    """Delete an appointment."""
    try:
        service.delete_appointment(appointment_id)
        return None
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
