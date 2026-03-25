"""
Service layer for doctor-related business logic.

This module implements the service layer for doctor operations, separating
business logic from route handlers.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.exceptions import (
    DuplicateResourceError,
    ResourceNotFoundError,
    ValidationError,
)
from backend.logging_config import BusinessLogger
from backend.utils import validate_phone, validate_email


class DoctorRepository:
    """Repository for doctor data access."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, doctor_data: schemas.DoctorCreate) -> models.Doctor:
        """Create a new doctor."""
        db_doctor = models.Doctor(**doctor_data.model_dump())
        self.db.add(db_doctor)
        self.db.commit()
        self.db.refresh(db_doctor)
        return db_doctor

    def get_by_id(self, doctor_id: int) -> Optional[models.Doctor]:
        """Get doctor by ID."""
        return (
            self.db.query(models.Doctor)
            .filter(models.Doctor.doctor_id == doctor_id)
            .first()
        )

    def get_by_email(self, email: str) -> Optional[models.Doctor]:
        """Get doctor by email."""
        return self.db.query(models.Doctor).filter(models.Doctor.email == email).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[models.Doctor]:
        """List all doctors."""
        return self.db.query(models.Doctor).offset(skip).limit(limit).all()

    def list_by_specialization(
        self, specialization: str, skip: int = 0, limit: int = 100
    ) -> List[models.Doctor]:
        """List doctors by specialization."""
        return (
            self.db.query(models.Doctor)
            .filter(models.Doctor.specialization.ilike(f"%{specialization}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_available(self, skip: int = 0, limit: int = 100) -> List[models.Doctor]:
        """List available doctors."""
        return (
            self.db.query(models.Doctor)
            .filter(models.Doctor.is_available.is_(True))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self, doctor_id: int, update_data: schemas.DoctorUpdate
    ) -> models.Doctor:
        """Update doctor."""
        doctor = self.get_by_id(doctor_id)
        if not doctor:
            raise ResourceNotFoundError("Doctor", doctor_id)

        for field, value in update_data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(doctor, field, value)

        self.db.commit()
        self.db.refresh(doctor)
        return doctor

    def delete(self, doctor_id: int) -> bool:
        """Delete doctor."""
        doctor = self.get_by_id(doctor_id)
        if not doctor:
            raise ResourceNotFoundError("Doctor", doctor_id)

        self.db.delete(doctor)
        self.db.commit()
        return True

    def count(self) -> int:
        """Get total doctor count."""
        return self.db.query(models.Doctor).count()


class DoctorService:
    """Business logic service for doctor operations."""

    def __init__(self, repository: DoctorRepository):
        self.repository = repository
        self.logger = BusinessLogger()

    def create_doctor(self, doctor_data: schemas.DoctorCreate) -> schemas.Doctor:
        """
        Create a new doctor with validation.

        Performs business logic validation before creating the doctor.
        """
        # Validate email
        if not validate_email(doctor_data.email):
            raise ValidationError(
                "Invalid email format", field_errors={"email": "Invalid email address"}
            )

        # Check for duplicate
        existing = self.repository.get_by_email(doctor_data.email)
        if existing:
            self.logger.log_duplicate_detection("Doctor", "email")
            raise DuplicateResourceError("Doctor", "email", doctor_data.email)

        # Validate phone
        if not validate_phone(doctor_data.phone):
            raise ValidationError(
                "Invalid phone number format",
                field_errors={"phone": "Phone number must be 10-15 digits"},
            )

        # Validate consultation fee
        if doctor_data.consultation_fee <= 0:
            raise ValidationError(
                "Invalid consultation fee",
                field_errors={
                    "consultation_fee": "Consultation fee must be greater than 0"
                },
            )

        doctor = self.repository.create(doctor_data)
        self.logger.log_operation("Doctor created", f"ID: {doctor.doctor_id}")

        return schemas.Doctor.model_validate(doctor)

    def get_doctor(self, doctor_id: int) -> schemas.Doctor:
        """Get a single doctor."""
        doctor = self.repository.get_by_id(doctor_id)
        if not doctor:
            raise ResourceNotFoundError("Doctor", doctor_id)

        return schemas.Doctor.model_validate(doctor)

    def list_doctors(self, skip: int = 0, limit: int = 100) -> List[schemas.Doctor]:
        """List all doctors."""
        doctors = self.repository.list_all(skip=skip, limit=limit)
        return [schemas.Doctor.model_validate(d) for d in doctors]

    def list_doctors_by_specialization(
        self, specialization: str, skip: int = 0, limit: int = 100
    ) -> List[schemas.Doctor]:
        """List doctors by specialization."""
        if not specialization or len(specialization) < 2:
            raise ValidationError("Specialization must be at least 2 characters")

        doctors = self.repository.list_by_specialization(
            specialization, skip=skip, limit=limit
        )
        return [schemas.Doctor.model_validate(d) for d in doctors]

    def list_available_doctors(
        self, skip: int = 0, limit: int = 100
    ) -> List[schemas.Doctor]:
        """List available doctors."""
        doctors = self.repository.list_available(skip=skip, limit=limit)
        return [schemas.Doctor.model_validate(d) for d in doctors]

    def update_doctor(
        self, doctor_id: int, update_data: schemas.DoctorUpdate
    ) -> schemas.Doctor:
        """Update an existing doctor."""
        # Verify doctor exists
        _ = self.repository.get_by_id(doctor_id)
        if not _:
            raise ResourceNotFoundError("Doctor", doctor_id)

        # Validate consultation fee if provided
        if (
            update_data.consultation_fee is not None
            and update_data.consultation_fee <= 0
        ):
            raise ValidationError(
                "Invalid consultation fee",
                field_errors={
                    "consultation_fee": "Consultation fee must be greater than 0"
                },
            )

        doctor = self.repository.update(doctor_id, update_data)
        self.logger.log_operation("Doctor updated", f"ID: {doctor_id}")

        return schemas.Doctor.model_validate(doctor)

    def delete_doctor(self, doctor_id: int) -> bool:
        """Delete a doctor."""
        result = self.repository.delete(doctor_id)
        if result:
            self.logger.log_operation("Doctor deleted", f"ID: {doctor_id}")
        return result

    def set_doctor_availability(
        self, doctor_id: int, is_available: bool
    ) -> schemas.Doctor:
        """Set doctor availability status."""
        doctor = self.repository.get_by_id(doctor_id)
        if not doctor:
            raise ResourceNotFoundError("Doctor", doctor_id)

        doctor.is_available = is_available
        self.repository.db.commit()
        self.repository.db.refresh(doctor)

        status = "available" if is_available else "unavailable"
        self.logger.log_operation(
            "Doctor availability updated", f"ID: {doctor_id}, Status: {status}"
        )

        return schemas.Doctor.model_validate(doctor)
