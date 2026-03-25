"""
Service layer for patient-related business logic.

This module implements the service layer for patient operations, separating
business logic from route handlers.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from backend import models, schemas
from backend.exceptions import (
    DuplicateResourceError,
    ResourceNotFoundError,
    ValidationError,
)
from backend.logging_config import BusinessLogger
from backend.utils import validate_phone, validate_email


class PatientRepository:
    """Repository for patient data access."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, patient_data: schemas.PatientCreate) -> models.Patient:
        """Create a new patient."""
        db_patient = models.Patient(**patient_data.model_dump())
        self.db.add(db_patient)
        self.db.commit()
        self.db.refresh(db_patient)
        return db_patient

    def get_by_id(self, patient_id: int) -> Optional[models.Patient]:
        """Get patient by ID."""
        return (
            self.db.query(models.Patient)
            .filter(models.Patient.patient_id == patient_id)
            .first()
        )

    def get_by_phone(self, phone: str) -> Optional[models.Patient]:
        """Get patient by phone number."""
        return (
            self.db.query(models.Patient).filter(models.Patient.phone == phone).first()
        )

    def list_all(self, skip: int = 0, limit: int = 100) -> List[models.Patient]:
        """List all patients with pagination."""
        return self.db.query(models.Patient).offset(skip).limit(limit).all()

    def search(
        self, query: str, skip: int = 0, limit: int = 100
    ) -> List[models.Patient]:
        """Search patients by name or phone."""
        like_pattern = f"%{query}%"
        return (
            self.db.query(models.Patient)
            .filter(
                or_(
                    models.Patient.first_name.ilike(like_pattern),
                    models.Patient.last_name.ilike(like_pattern),
                    models.Patient.phone.ilike(like_pattern),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self, patient_id: int, update_data: schemas.PatientUpdate
    ) -> models.Patient:
        """Update patient."""
        patient = self.get_by_id(patient_id)
        if not patient:
            raise ResourceNotFoundError("Patient", patient_id)

        for field, value in update_data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(patient, field, value)

        self.db.commit()
        self.db.refresh(patient)
        return patient

    def delete(self, patient_id: int) -> bool:
        """Delete patient."""
        patient = self.get_by_id(patient_id)
        if not patient:
            raise ResourceNotFoundError("Patient", patient_id)

        self.db.delete(patient)
        self.db.commit()
        return True

    def count(self) -> int:
        """Get total patient count."""
        return self.db.query(models.Patient).count()

    def get_recent_doctor(self, patient_id: int) -> Optional[models.Doctor]:
        """Get the most recent doctor for a patient from medical records."""
        recent_record = (
            self.db.query(models.MedicalRecord)
            .filter(models.MedicalRecord.patient_id == patient_id)
            .order_by(desc(models.MedicalRecord.record_date))
            .first()
        )
        if recent_record:
            return recent_record.doctor

        # Fallback to most recent appointment if no medical record exists
        recent_appointment = (
            self.db.query(models.Appointment)
            .filter(models.Appointment.patient_id == patient_id)
            .order_by(desc(models.Appointment.appointment_date))
            .first()
        )
        if recent_appointment:
            return recent_appointment.doctor

        return None


class PatientService:
    """Business logic service for patient operations."""

    def __init__(self, repository: PatientRepository):
        self.repository = repository
        self.logger = BusinessLogger()

    def create_patient(self, patient_data: schemas.PatientCreate) -> schemas.Patient:
        """
        Create a new patient with validation.

        Performs business logic validation before creating the patient.
        """
        # Validate phone format
        if not validate_phone(patient_data.phone):
            raise ValidationError(
                "Invalid phone number format",
                field_errors={"phone": "Phone number must be 10-15 digits"},
            )

        # Check for duplicate
        existing = self.repository.get_by_phone(patient_data.phone)
        if existing:
            self.logger.log_duplicate_detection("Patient", "phone")
            raise DuplicateResourceError("Patient", "phone", patient_data.phone)

        # Validate email if provided
        if patient_data.email and not validate_email(patient_data.email):
            raise ValidationError(
                "Invalid email format", field_errors={"email": "Invalid email address"}
            )

        # Create patient
        patient = self.repository.create(patient_data)
        self.logger.log_operation("Patient created", f"ID: {patient.patient_id}")

        return schemas.Patient.model_validate(patient)

    def get_patient(self, patient_id: int) -> schemas.Patient:
        """Get a single patient."""
        patient = self.repository.get_by_id(patient_id)
        if not patient:
            raise ResourceNotFoundError("Patient", patient_id)

        return schemas.Patient.model_validate(patient)

    def list_patients(self, skip: int = 0, limit: int = 100) -> List[schemas.Patient]:
        """List all patients."""
        patients = self.repository.list_all(skip=skip, limit=limit)
        return [schemas.Patient.model_validate(p) for p in patients]

    def search_patients(
        self, query: str, skip: int = 0, limit: int = 100
    ) -> List[schemas.Patient]:
        """Search patients."""
        if not query or len(query) < 2:
            raise ValidationError("Search query must be at least 2 characters")

        patients = self.repository.search(query, skip=skip, limit=limit)
        return [schemas.Patient.model_validate(p) for p in patients]

    def update_patient(
        self, patient_id: int, update_data: schemas.PatientUpdate
    ) -> schemas.Patient:
        """Update an existing patient."""
        # Verify patient exists
        _ = self.repository.get_by_id(patient_id)
        if not _:
            raise ResourceNotFoundError("Patient", patient_id)

        # Validate phone if being updated
        if update_data.phone and not validate_phone(update_data.phone):
            raise ValidationError(
                "Invalid phone number format",
                field_errors={"phone": "Phone number must be 10-15 digits"},
            )

        # Check for duplicate phone
        if update_data.phone:
            existing = (
                self.repository.db.query(models.Patient)
                .filter(
                    models.Patient.phone == update_data.phone,
                    models.Patient.patient_id != patient_id,
                )
                .first()
            )
            if existing:
                self.logger.log_duplicate_detection("Patient", "phone")
                raise DuplicateResourceError("Patient", "phone", update_data.phone)

        patient = self.repository.update(patient_id, update_data)
        self.logger.log_operation("Patient updated", f"ID: {patient_id}")

        return schemas.Patient.model_validate(patient)

    def delete_patient(self, patient_id: int) -> bool:
        """Delete a patient."""
        result = self.repository.delete(patient_id)
        if result:
            self.logger.log_operation("Patient deleted", f"ID: {patient_id}")
        return result

    def get_patient_stats(self) -> Dict[str, Any]:
        """Get patient statistics."""
        total_count = self.repository.count()
        return {
            "total_patients": total_count,
            "active_patients": total_count,  # Could be refined with additional logic
        }

    def get_patient_with_doctor(self, patient_id: int) -> Dict[str, Any]:
        """Get patient with their most recent doctor information."""
        patient = self.repository.get_by_id(patient_id)
        if not patient:
            raise ResourceNotFoundError("Patient", patient_id)

        doctor = self.repository.get_recent_doctor(patient_id)

        return {
            "patient": schemas.Patient.model_validate(patient),
            "doctor": schemas.DoctorShort.model_validate(doctor) if doctor else None,
        }
