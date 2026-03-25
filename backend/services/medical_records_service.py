"""
Service layer for medical record-related business logic.

This module implements the service layer for medical record operations, separating
business logic from route handlers.
"""

from typing import Optional, List
from sqlalchemy.orm import Session, selectinload

from backend import models, schemas
from backend.exceptions import (
    ResourceNotFoundError,
)
from backend.logging_config import BusinessLogger


class MedicalRecordRepository:
    """Repository for medical record data access."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, record_data: schemas.MedicalRecordCreate) -> models.MedicalRecord:
        """Create a new medical record."""
        db_record = models.MedicalRecord(**record_data.model_dump())
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def get_by_id(self, record_id: int) -> Optional[models.MedicalRecord]:
        """Get medical record by ID with relationships."""
        return (
            self.db.query(models.MedicalRecord)
            .options(
                selectinload(models.MedicalRecord.patient),
                selectinload(models.MedicalRecord.doctor),
            )
            .filter(models.MedicalRecord.record_id == record_id)
            .first()
        )

    def list_all(self, skip: int = 0, limit: int = 100) -> List[models.MedicalRecord]:
        """List all medical records."""
        return (
            self.db.query(models.MedicalRecord)
            .options(
                selectinload(models.MedicalRecord.patient),
                selectinload(models.MedicalRecord.doctor),
            )
            .order_by(models.MedicalRecord.record_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_patient(
        self, patient_id: int, skip: int = 0, limit: int = 100
    ) -> List[models.MedicalRecord]:
        """Get medical records for a patient."""
        return (
            self.db.query(models.MedicalRecord)
            .filter(models.MedicalRecord.patient_id == patient_id)
            .order_by(models.MedicalRecord.record_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_doctor(
        self, doctor_id: int, skip: int = 0, limit: int = 100
    ) -> List[models.MedicalRecord]:
        """Get medical records created by a doctor."""
        return (
            self.db.query(models.MedicalRecord)
            .filter(models.MedicalRecord.doctor_id == doctor_id)
            .order_by(models.MedicalRecord.record_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self, record_id: int, update_data: schemas.MedicalRecordUpdate
    ) -> models.MedicalRecord:
        """Update medical record."""
        record = self.get_by_id(record_id)
        if not record:
            raise ResourceNotFoundError("MedicalRecord", record_id)

        for field, value in update_data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(record, field, value)

        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record_id: int) -> bool:
        """Delete medical record."""
        record = self.get_by_id(record_id)
        if not record:
            raise ResourceNotFoundError("MedicalRecord", record_id)

        self.db.delete(record)
        self.db.commit()
        return True

    def count(self) -> int:
        """Get total medical record count."""
        return self.db.query(models.MedicalRecord).count()


class MedicalRecordService:
    """Business logic service for medical record operations."""

    def __init__(self, repository: MedicalRecordRepository, db: Session):
        self.repository = repository
        self.db = db
        self.logger = BusinessLogger()

    def create_medical_record(
        self, record_data: schemas.MedicalRecordCreate
    ) -> schemas.MedicalRecord:
        """
        Create a new medical record with validation.

        Validates:
        - Patient exists
        - Doctor exists
        - Appointment exists (if provided)
        """
        # Verify patient exists
        patient = (
            self.db.query(models.Patient)
            .filter(models.Patient.patient_id == record_data.patient_id)
            .first()
        )
        if not patient:
            raise ResourceNotFoundError("Patient", record_data.patient_id)

        # Verify doctor exists
        doctor = (
            self.db.query(models.Doctor)
            .filter(models.Doctor.doctor_id == record_data.doctor_id)
            .first()
        )
        if not doctor:
            raise ResourceNotFoundError("Doctor", record_data.doctor_id)

        # Verify appointment if provided
        if record_data.appointment_id:
            appointment = (
                self.db.query(models.Appointment)
                .filter(models.Appointment.appointment_id == record_data.appointment_id)
                .first()
            )
            if not appointment:
                raise ResourceNotFoundError("Appointment", record_data.appointment_id)

        record = self.repository.create(record_data)
        self.logger.log_operation("Medical record created", f"ID: {record.record_id}")

        # Refresh and return
        self.db.refresh(record)
        return schemas.MedicalRecord.model_validate(record)

    def get_medical_record(self, record_id: int) -> schemas.MedicalRecord:
        """Get a single medical record."""
        record = self.repository.get_by_id(record_id)
        if not record:
            raise ResourceNotFoundError("MedicalRecord", record_id)

        return schemas.MedicalRecord.model_validate(record)

    def list_medical_records(
        self, skip: int = 0, limit: int = 100
    ) -> List[schemas.MedicalRecord]:
        """List all medical records."""
        records = self.repository.list_all(skip=skip, limit=limit)
        return [schemas.MedicalRecord.model_validate(r) for r in records]

    def get_patient_medical_records(
        self, patient_id: int, skip: int = 0, limit: int = 100
    ) -> List[schemas.MedicalRecord]:
        """Get medical records for a patient."""
        # Verify patient exists
        patient = (
            self.db.query(models.Patient)
            .filter(models.Patient.patient_id == patient_id)
            .first()
        )
        if not patient:
            raise ResourceNotFoundError("Patient", patient_id)

        records = self.repository.get_by_patient(patient_id, skip=skip, limit=limit)
        return [schemas.MedicalRecord.model_validate(r) for r in records]

    def get_doctor_medical_records(
        self, doctor_id: int, skip: int = 0, limit: int = 100
    ) -> List[schemas.MedicalRecord]:
        """Get medical records created by a doctor."""
        # Verify doctor exists
        doctor = (
            self.db.query(models.Doctor)
            .filter(models.Doctor.doctor_id == doctor_id)
            .first()
        )
        if not doctor:
            raise ResourceNotFoundError("Doctor", doctor_id)

        records = self.repository.get_by_doctor(doctor_id, skip=skip, limit=limit)
        return [schemas.MedicalRecord.model_validate(r) for r in records]

    def update_medical_record(
        self, record_id: int, update_data: schemas.MedicalRecordUpdate
    ) -> schemas.MedicalRecord:
        """Update an existing medical record."""
        # Verify record exists
        _ = self.repository.get_by_id(record_id)
        if not _:
            raise ResourceNotFoundError("MedicalRecord", record_id)

        record = self.repository.update(record_id, update_data)
        self.logger.log_operation("Medical record updated", f"ID: {record_id}")

        return schemas.MedicalRecord.model_validate(record)

    def delete_medical_record(self, record_id: int) -> bool:
        """Delete a medical record."""
        result = self.repository.delete(record_id)
        if result:
            self.logger.log_operation("Medical record deleted", f"ID: {record_id}")
        return result
