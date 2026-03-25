from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import schemas
from backend.services import PatientService, PatientRepository
from backend.exceptions import APIException

router = APIRouter(prefix="/patients", tags=["Patients"])


def get_patient_service(db: Session = Depends(get_db)) -> PatientService:
    """Dependency injection for PatientService."""
    return PatientService(PatientRepository(db))


@router.get("/", response_model=List[schemas.Patient])
def list_patients(
    search: str = Query(None, description="Search by name or phone"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: PatientService = Depends(get_patient_service),
):
    """List all patients with optional search."""
    try:
        if search:
            return service.search_patients(search, skip=skip, limit=limit)
        return service.list_patients(skip=skip, limit=limit)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/", response_model=schemas.Patient, status_code=201)
def create_patient(
    patient: schemas.PatientCreate,
    service: PatientService = Depends(get_patient_service),
):
    """Create a new patient."""
    try:
        return service.create_patient(patient)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/stats", response_model=dict)
def get_patient_stats(
    service: PatientService = Depends(get_patient_service),
):
    """Get patient statistics."""
    try:
        return service.get_patient_stats()
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{patient_id}/with-doctor", response_model=dict)
def get_patient_with_doctor(
    patient_id: int,
    service: PatientService = Depends(get_patient_service),
):
    """Get patient with their most recent doctor information."""
    try:
        return service.get_patient_with_doctor(patient_id)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{patient_id}", response_model=schemas.Patient)
def get_patient(
    patient_id: int,
    service: PatientService = Depends(get_patient_service),
):
    """Get a single patient."""
    try:
        return service.get_patient(patient_id)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{patient_id}", response_model=schemas.Patient)
def update_patient(
    patient_id: int,
    update: schemas.PatientUpdate,
    service: PatientService = Depends(get_patient_service),
):
    """Update a patient."""
    try:
        return service.update_patient(patient_id, update)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{patient_id}", status_code=204)
def delete_patient(
    patient_id: int,
    service: PatientService = Depends(get_patient_service),
):
    """Delete a patient."""
    try:
        service.delete_patient(patient_id)
        return None
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
