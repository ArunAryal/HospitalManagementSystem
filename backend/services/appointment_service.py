"""
Service layer for appointment-related business logic.

This module implements the service layer for appointment operations, separating
business logic from route handlers.
"""

from typing import Optional, List
from datetime import date, time
from sqlalchemy.orm import Session, selectinload

from backend import models, schemas
from backend.exceptions import (
    DuplicateResourceError,
    ResourceNotFoundError,
    ValidationError,
    InvalidOperationError,
)
from backend.logging_config import BusinessLogger
from backend.utils import validate_future_date


class AppointmentRepository:
    """Repository for appointment data access."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, appointment_data: schemas.AppointmentCreate) -> models.Appointment:
        """Create a new appointment."""
        db_appt = models.Appointment(**appointment_data.model_dump())
        self.db.add(db_appt)
        self.db.commit()
        self.db.refresh(db_appt)
        return db_appt

    def get_by_id(self, appointment_id: int) -> Optional[models.Appointment]:
        """Get appointment by ID with relationships."""
        return (
            self.db.query(models.Appointment)
            .options(
                selectinload(models.Appointment.patient),
                selectinload(models.Appointment.doctor),
            )
            .filter(models.Appointment.appointment_id == appointment_id)
            .first()
        )

    def list_all(self, skip: int = 0, limit: int = 100) -> List[models.Appointment]:
        """List all appointments."""
        return (
            self.db.query(models.Appointment)
            .options(
                selectinload(models.Appointment.patient),
                selectinload(models.Appointment.doctor),
            )
            .order_by(
                models.Appointment.appointment_date, models.Appointment.appointment_time
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_doctor_date_time(
        self,
        doctor_id: int,
        appointment_date: date,
        appointment_time: time,
        exclude_appointment_id: Optional[int] = None,
    ) -> Optional[models.Appointment]:
        """Check if a doctor has an appointment at the given date and time."""
        query = self.db.query(models.Appointment).filter(
            models.Appointment.doctor_id == doctor_id,
            models.Appointment.appointment_date == appointment_date,
            models.Appointment.appointment_time == appointment_time,
            models.Appointment.status == models.AppointmentStatus.Scheduled,
        )

        if exclude_appointment_id:
            query = query.filter(
                models.Appointment.appointment_id != exclude_appointment_id
            )

        return query.first()

    def get_by_patient(
        self, patient_id: int, skip: int = 0, limit: int = 100
    ) -> List[models.Appointment]:
        """Get appointments for a patient."""
        return (
            self.db.query(models.Appointment)
            .filter(models.Appointment.patient_id == patient_id)
            .order_by(models.Appointment.appointment_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_doctor(
        self, doctor_id: int, skip: int = 0, limit: int = 100
    ) -> List[models.Appointment]:
        """Get appointments for a doctor."""
        return (
            self.db.query(models.Appointment)
            .filter(models.Appointment.doctor_id == doctor_id)
            .order_by(models.Appointment.appointment_date)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self, appointment_id: int, update_data: schemas.AppointmentUpdate
    ) -> models.Appointment:
        """Update appointment."""
        appt = self.get_by_id(appointment_id)
        if not appt:
            raise ResourceNotFoundError("Appointment", appointment_id)

        for field, value in update_data.model_dump(exclude_unset=True).items():
            if value is not None:
                if field == "status" and isinstance(value, str):
                    value = models.AppointmentStatus(value)
                setattr(appt, field, value)

        self.db.commit()
        self.db.refresh(appt)
        return appt

    def delete(self, appointment_id: int) -> bool:
        """Delete appointment."""
        appt = self.get_by_id(appointment_id)
        if not appt:
            raise ResourceNotFoundError("Appointment", appointment_id)

        self.db.delete(appt)
        self.db.commit()
        return True

    def count(self) -> int:
        """Get total appointment count."""
        return self.db.query(models.Appointment).count()


class AppointmentService:
    """Business logic service for appointment operations."""

    def __init__(self, repository: AppointmentRepository, db: Session):
        self.repository = repository
        self.db = db
        self.logger = BusinessLogger()

    def create_appointment(
        self, appt_data: schemas.AppointmentCreate
    ) -> schemas.Appointment:
        """
        Create a new appointment with business logic validation.

        Validates:
        - Patient exists
        - Doctor exists and is available
        - No conflicting appointments for the doctor
        - Appointment date is in the future
        """
        # Verify patient exists
        patient = (
            self.db.query(models.Patient)
            .filter(models.Patient.patient_id == appt_data.patient_id)
            .first()
        )
        if not patient:
            raise ResourceNotFoundError("Patient", appt_data.patient_id)

        # Verify doctor exists
        doctor = (
            self.db.query(models.Doctor)
            .filter(models.Doctor.doctor_id == appt_data.doctor_id)
            .first()
        )
        if not doctor:
            raise ResourceNotFoundError("Doctor", appt_data.doctor_id)

        # Check doctor availability
        if not doctor.is_available:
            raise InvalidOperationError("Doctor is not currently available")

        # Validate appointment date is in the future
        if not validate_future_date(appt_data.appointment_date):
            raise ValidationError(
                "Invalid appointment date",
                field_errors={
                    "appointment_date": "Appointment date must be in the future"
                },
            )

        # Check for conflicting appointments
        conflict = self.repository.get_by_doctor_date_time(
            doctor_id=appt_data.doctor_id,
            appointment_date=appt_data.appointment_date,
            appointment_time=appt_data.appointment_time,
        )
        if conflict:
            self.logger.log_duplicate_detection("Appointment", "doctor_time_slot")
            raise DuplicateResourceError(
                "Appointment",
                "doctor_time_slot",
                f"{appt_data.doctor_id} at {appt_data.appointment_date} {appt_data.appointment_time}",
            )

        # Create appointment
        appointment = self.repository.create(appt_data)

        # Create bill for appointment
        bill = models.Bill(
            patient_id=appt_data.patient_id,
            appointment_id=appointment.appointment_id,
            consultation_fee=doctor.consultation_fee,
            medicine_charges=0,
            room_charges=0,
            other_charges=0,
            total_amount=doctor.consultation_fee,
            payment_status=models.PaymentStatus.Pending,
        )
        self.db.add(bill)
        self.db.commit()

        self.logger.log_operation(
            "Appointment created", f"ID: {appointment.appointment_id}"
        )

        # Refresh to get relationships
        self.db.refresh(appointment)
        return schemas.Appointment.model_validate(appointment)

    def get_appointment(self, appointment_id: int) -> schemas.Appointment:
        """Get a single appointment."""
        appointment = self.repository.get_by_id(appointment_id)
        if not appointment:
            raise ResourceNotFoundError("Appointment", appointment_id)

        return schemas.Appointment.model_validate(appointment)

    def list_appointments(
        self, skip: int = 0, limit: int = 100
    ) -> List[schemas.Appointment]:
        """List all appointments."""
        appointments = self.repository.list_all(skip=skip, limit=limit)
        return [schemas.Appointment.model_validate(a) for a in appointments]

    def get_patient_appointments(
        self, patient_id: int, skip: int = 0, limit: int = 100
    ) -> List[schemas.Appointment]:
        """Get appointments for a patient."""
        # Verify patient exists
        patient = (
            self.db.query(models.Patient)
            .filter(models.Patient.patient_id == patient_id)
            .first()
        )
        if not patient:
            raise ResourceNotFoundError("Patient", patient_id)

        appointments = self.repository.get_by_patient(
            patient_id, skip=skip, limit=limit
        )
        return [schemas.Appointment.model_validate(a) for a in appointments]

    def get_doctor_appointments(
        self, doctor_id: int, skip: int = 0, limit: int = 100
    ) -> List[schemas.Appointment]:
        """Get appointments for a doctor."""
        # Verify doctor exists
        doctor = (
            self.db.query(models.Doctor)
            .filter(models.Doctor.doctor_id == doctor_id)
            .first()
        )
        if not doctor:
            raise ResourceNotFoundError("Doctor", doctor_id)

        appointments = self.repository.get_by_doctor(doctor_id, skip=skip, limit=limit)
        return [schemas.Appointment.model_validate(a) for a in appointments]

    def update_appointment(
        self, appointment_id: int, update_data: schemas.AppointmentUpdate
    ) -> schemas.Appointment:
        """Update an appointment."""
        # Verify appointment exists
        _ = self.repository.get_by_id(appointment_id)
        if not _:
            raise ResourceNotFoundError("Appointment", appointment_id)

        # Validate new date if being changed
        if update_data.appointment_date and not validate_future_date(
            update_data.appointment_date
        ):
            raise ValidationError(
                "Invalid appointment date",
                field_errors={
                    "appointment_date": "Appointment date must be in the future"
                },
            )

        appointment = self.repository.update(appointment_id, update_data)
        self.logger.log_operation("Appointment updated", f"ID: {appointment_id}")

        return schemas.Appointment.model_validate(appointment)

    def cancel_appointment(self, appointment_id: int) -> schemas.Appointment:
        """Cancel an appointment."""
        appointment = self.repository.get_by_id(appointment_id)
        if not appointment:
            raise ResourceNotFoundError("Appointment", appointment_id)

        if appointment.status == models.AppointmentStatus.Cancelled:
            raise InvalidOperationError("Appointment is already cancelled")

        appointment.status = models.AppointmentStatus.Cancelled
        self.db.commit()
        self.db.refresh(appointment)

        self.logger.log_operation("Appointment cancelled", f"ID: {appointment_id}")

        return schemas.Appointment.model_validate(appointment)

    def delete_appointment(self, appointment_id: int) -> bool:
        """Delete an appointment."""
        result = self.repository.delete(appointment_id)
        if result:
            self.logger.log_operation("Appointment deleted", f"ID: {appointment_id}")
        return result
