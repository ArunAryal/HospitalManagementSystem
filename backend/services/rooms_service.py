"""
Service layer for room and admission-related business logic.

This module implements the service layer for room and admission operations,
separating business logic from route handlers.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.exceptions import (
    ResourceNotFoundError,
    ValidationError,
    InvalidOperationError,
)
from backend.logging_config import BusinessLogger


class RoomRepository:
    """Repository for room data access."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, room_data: schemas.RoomCreate) -> models.Room:
        """Create a new room."""
        db_room = models.Room(**room_data.model_dump())
        self.db.add(db_room)
        self.db.commit()
        self.db.refresh(db_room)
        return db_room

    def get_by_id(self, room_id: int) -> Optional[models.Room]:
        """Get room by ID."""
        return self.db.query(models.Room).filter(models.Room.room_id == room_id).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[models.Room]:
        """List all rooms."""
        return (
            self.db.query(models.Room)
            .order_by(models.Room.room_number)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_type(
        self, room_type: str, skip: int = 0, limit: int = 100
    ) -> List[models.Room]:
        """Get rooms by type."""
        return (
            self.db.query(models.Room)
            .filter(models.Room.room_type == room_type)
            .order_by(models.Room.room_number)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_available(self, skip: int = 0, limit: int = 100) -> List[models.Room]:
        """Get available rooms (occupancy < capacity)."""
        return (
            self.db.query(models.Room)
            .filter(models.Room.occupancy < models.Room.capacity)
            .order_by(models.Room.room_number)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, room_id: int, update_data: schemas.RoomUpdate) -> models.Room:
        """Update room."""
        room = self.get_by_id(room_id)
        if not room:
            raise ResourceNotFoundError("Room", room_id)

        for field, value in update_data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(room, field, value)

        self.db.commit()
        self.db.refresh(room)
        return room

    def update_occupancy(self, room_id: int, occupancy: int) -> models.Room:
        """Update room occupancy."""
        room = self.get_by_id(room_id)
        if not room:
            raise ResourceNotFoundError("Room", room_id)

        room.occupancy = occupancy
        self.db.commit()
        self.db.refresh(room)
        return room

    def delete(self, room_id: int) -> bool:
        """Delete room."""
        room = self.get_by_id(room_id)
        if not room:
            raise ResourceNotFoundError("Room", room_id)

        self.db.delete(room)
        self.db.commit()
        return True

    def count(self) -> int:
        """Get total room count."""
        return self.db.query(models.Room).count()


class AdmissionRepository:
    """Repository for admission data access."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, admission_data: schemas.AdmissionCreate) -> models.Admission:
        """Create a new admission record."""
        db_admission = models.Admission(**admission_data.model_dump())
        self.db.add(db_admission)
        self.db.commit()
        self.db.refresh(db_admission)
        return db_admission

    def get_by_id(self, admission_id: int) -> Optional[models.Admission]:
        """Get admission by ID with relationships."""
        return (
            self.db.query(models.Admission)
            .filter(models.Admission.admission_id == admission_id)
            .first()
        )

    def list_all(self, skip: int = 0, limit: int = 100) -> List[models.Admission]:
        """List all admissions."""
        return (
            self.db.query(models.Admission)
            .order_by(models.Admission.admission_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_patient(
        self, patient_id: int, skip: int = 0, limit: int = 100
    ) -> List[models.Admission]:
        """Get admissions for a patient."""
        return (
            self.db.query(models.Admission)
            .filter(models.Admission.patient_id == patient_id)
            .order_by(models.Admission.admission_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_admissions(
        self, skip: int = 0, limit: int = 100
    ) -> List[models.Admission]:
        """Get currently active admissions (discharge_date is NULL)."""
        return (
            self.db.query(models.Admission)
            .filter(models.Admission.discharge_date.is_(None))
            .order_by(models.Admission.admission_date)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_room(
        self, room_id: int, skip: int = 0, limit: int = 100
    ) -> List[models.Admission]:
        """Get admissions in a specific room."""
        return (
            self.db.query(models.Admission)
            .filter(models.Admission.room_id == room_id)
            .order_by(models.Admission.admission_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self, admission_id: int, update_data: schemas.AdmissionUpdate
    ) -> models.Admission:
        """Update admission record."""
        admission = self.get_by_id(admission_id)
        if not admission:
            raise ResourceNotFoundError("Admission", admission_id)

        for field, value in update_data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(admission, field, value)

        self.db.commit()
        self.db.refresh(admission)
        return admission

    def delete(self, admission_id: int) -> bool:
        """Delete admission record."""
        admission = self.get_by_id(admission_id)
        if not admission:
            raise ResourceNotFoundError("Admission", admission_id)

        self.db.delete(admission)
        self.db.commit()
        return True


class RoomService:
    """Business logic service for room operations."""

    def __init__(self, room_repository: RoomRepository, db: Session):
        self.repository = room_repository
        self.db = db
        self.logger = BusinessLogger()

    def create_room(self, room_data: schemas.RoomCreate) -> schemas.Room:
        """
        Create a new room with validation.

        Validates:
        - Capacity is positive
        - Occupancy does not exceed capacity
        """
        if room_data.capacity <= 0:
            raise ValidationError(
                "Invalid capacity",
                field_errors={"capacity": "Capacity must be greater than 0"},
            )

        if room_data.occupancy > room_data.capacity:
            raise ValidationError(
                "Invalid occupancy",
                field_errors={"occupancy": "Occupancy cannot exceed capacity"},
            )

        room = self.repository.create(room_data)
        self.logger.log_operation(
            "Room created", f"ID: {room.room_id}, Number: {room.room_number}"
        )

        return schemas.Room.model_validate(room)

    def get_room(self, room_id: int) -> schemas.Room:
        """Get a single room."""
        room = self.repository.get_by_id(room_id)
        if not room:
            raise ResourceNotFoundError("Room", room_id)

        return schemas.Room.model_validate(room)

    def list_rooms(self, skip: int = 0, limit: int = 100) -> List[schemas.Room]:
        """List all rooms."""
        rooms = self.repository.list_all(skip=skip, limit=limit)
        return [schemas.Room.model_validate(r) for r in rooms]

    def list_rooms_by_type(
        self, room_type: str, skip: int = 0, limit: int = 100
    ) -> List[schemas.Room]:
        """List rooms by type."""
        rooms = self.repository.list_by_type(room_type, skip=skip, limit=limit)
        return [schemas.Room.model_validate(r) for r in rooms]

    def list_available_rooms(
        self, skip: int = 0, limit: int = 100
    ) -> List[schemas.Room]:
        """Get available rooms."""
        rooms = self.repository.list_available(skip=skip, limit=limit)
        return [schemas.Room.model_validate(r) for r in rooms]

    def update_room(
        self, room_id: int, update_data: schemas.RoomUpdate
    ) -> schemas.Room:
        """Update a room."""
        room = self.repository.get_by_id(room_id)
        if not room:
            raise ResourceNotFoundError("Room", room_id)

        # If updating capacity, ensure occupancy <= capacity
        if update_data.capacity is not None:
            if update_data.capacity <= 0:
                raise ValidationError(
                    "Invalid capacity",
                    field_errors={"capacity": "Capacity must be greater than 0"},
                )
            if room.occupancy > update_data.capacity:
                raise InvalidOperationError(
                    f"Cannot reduce capacity below current occupancy ({room.occupancy})"
                )

        room = self.repository.update(room_id, update_data)
        self.logger.log_operation("Room updated", f"ID: {room_id}")

        return schemas.Room.model_validate(room)

    def delete_room(self, room_id: int) -> bool:
        """Delete a room."""
        # Check if room has active admissions
        admissions = (
            self.db.query(models.Admission)
            .filter(
                models.Admission.room_id == room_id,
                models.Admission.discharge_date.is_(None),
            )
            .first()
        )

        if admissions:
            raise InvalidOperationError("Cannot delete room with active admissions")

        result = self.repository.delete(room_id)
        if result:
            self.logger.log_operation("Room deleted", f"ID: {room_id}")
        return result

    def get_room_occupancy_stats(self) -> Dict[str, Any]:
        """Get room occupancy statistics."""
        all_rooms = self.repository.list_all(skip=0, limit=999999)
        available_rooms = self.repository.list_available(skip=0, limit=999999)

        total_capacity = sum(r.capacity for r in all_rooms)
        total_occupancy = sum(r.occupancy for r in all_rooms)

        return {
            "total_rooms": self.repository.count(),
            "available_rooms": len(available_rooms),
            "total_capacity": total_capacity,
            "total_occupancy": total_occupancy,
            "occupancy_rate": (total_occupancy / total_capacity * 100)
            if total_capacity > 0
            else 0,
        }


class AdmissionService:
    """Business logic service for admission operations."""

    def __init__(
        self,
        admission_repository: AdmissionRepository,
        room_repository: RoomRepository,
        db: Session,
    ):
        self.repository = admission_repository
        self.room_repository = room_repository
        self.db = db
        self.logger = BusinessLogger()

    def admit_patient(
        self, admission_data: schemas.AdmissionCreate
    ) -> schemas.Admission:
        """
        Admit a patient with validation.

        Validates:
        - Patient exists
        - Doctor exists
        - Room exists and has capacity
        - Admission date is valid
        """
        # Verify patient
        patient = (
            self.db.query(models.Patient)
            .filter(models.Patient.patient_id == admission_data.patient_id)
            .first()
        )
        if not patient:
            raise ResourceNotFoundError("Patient", admission_data.patient_id)

        # Verify doctor
        doctor = (
            self.db.query(models.Doctor)
            .filter(models.Doctor.doctor_id == admission_data.doctor_id)
            .first()
        )
        if not doctor:
            raise ResourceNotFoundError("Doctor", admission_data.doctor_id)

        # Verify room exists and has capacity
        room = self.room_repository.get_by_id(admission_data.room_id)
        if not room:
            raise ResourceNotFoundError("Room", admission_data.room_id)

        if room.occupancy >= room.capacity:
            raise InvalidOperationError("Room is at full capacity")

        # Create admission
        admission = self.repository.create(admission_data)

        # Update room occupancy
        self.room_repository.update_occupancy(room.room_id, room.occupancy + 1)

        self.logger.log_operation(
            "Patient admitted",
            f"Patient ID: {admission.patient_id}, Room: {room.room_number}",
        )

        return schemas.Admission.model_validate(admission)

    def get_admission(self, admission_id: int) -> schemas.Admission:
        """Get a single admission."""
        admission = self.repository.get_by_id(admission_id)
        if not admission:
            raise ResourceNotFoundError("Admission", admission_id)

        return schemas.Admission.model_validate(admission)

    def list_admissions(
        self, skip: int = 0, limit: int = 100
    ) -> List[schemas.Admission]:
        """List all admissions."""
        admissions = self.repository.list_all(skip=skip, limit=limit)
        return [schemas.Admission.model_validate(a) for a in admissions]

    def get_patient_admissions(
        self, patient_id: int, skip: int = 0, limit: int = 100
    ) -> List[schemas.Admission]:
        """Get admissions for a patient."""
        # Verify patient
        patient = (
            self.db.query(models.Patient)
            .filter(models.Patient.patient_id == patient_id)
            .first()
        )
        if not patient:
            raise ResourceNotFoundError("Patient", patient_id)

        admissions = self.repository.get_by_patient(patient_id, skip=skip, limit=limit)
        return [schemas.Admission.model_validate(a) for a in admissions]

    def get_active_admissions(
        self, skip: int = 0, limit: int = 100
    ) -> List[schemas.Admission]:
        """Get currently active admissions."""
        admissions = self.repository.get_active_admissions(skip=skip, limit=limit)
        return [schemas.Admission.model_validate(a) for a in admissions]

    def discharge_patient(self, admission_id: int) -> schemas.Admission:
        """Discharge a patient from admission."""
        admission = self.repository.get_by_id(admission_id)
        if not admission:
            raise ResourceNotFoundError("Admission", admission_id)

        if admission.discharge_date is not None:
            raise InvalidOperationError("Patient already discharged")

        # Update discharge date
        update_data = schemas.AdmissionUpdate(discharge_date=datetime.now())
        admission = self.repository.update(admission_id, update_data)

        # Update room occupancy
        room = self.room_repository.get_by_id(admission.room_id)
        if room and room.occupancy > 0:
            self.room_repository.update_occupancy(room.room_id, room.occupancy - 1)

        self.logger.log_operation("Patient discharged", f"Admission ID: {admission_id}")

        return schemas.Admission.model_validate(admission)

    def update_admission(
        self, admission_id: int, update_data: schemas.AdmissionUpdate
    ) -> schemas.Admission:
        """Update an admission record."""
        admission = self.repository.get_by_id(admission_id)
        if not admission:
            raise ResourceNotFoundError("Admission", admission_id)

        # If updating room, verify new room has capacity
        if update_data.room_id is not None and update_data.room_id != admission.room_id:
            new_room = self.room_repository.get_by_id(update_data.room_id)
            if not new_room:
                raise ResourceNotFoundError("Room", update_data.room_id)

            if new_room.occupancy >= new_room.capacity:
                raise InvalidOperationError("New room is at full capacity")

            # Update occupancy in old and new rooms
            old_room = self.room_repository.get_by_id(admission.room_id)
            if old_room and old_room.occupancy > 0:
                self.room_repository.update_occupancy(
                    old_room.room_id, old_room.occupancy - 1
                )
            self.room_repository.update_occupancy(
                new_room.room_id, new_room.occupancy + 1
            )

        admission = self.repository.update(admission_id, update_data)
        self.logger.log_operation("Admission updated", f"ID: {admission_id}")

        return schemas.Admission.model_validate(admission)

    def delete_admission(self, admission_id: int) -> bool:
        """Delete an admission record."""
        admission = self.repository.get_by_id(admission_id)
        if not admission:
            raise ResourceNotFoundError("Admission", admission_id)

        result = self.repository.delete(admission_id)
        if result:
            self.logger.log_operation("Admission deleted", f"ID: {admission_id}")
        return result

    def get_admission_statistics(self) -> Dict[str, Any]:
        """Get admission statistics."""
        all_admissions = self.repository.list_all(skip=0, limit=999999)
        active_admissions = self.repository.get_active_admissions(skip=0, limit=999999)

        avg_length_of_stay = 0
        discharged_admissions = [
            a for a in all_admissions if a.discharge_date is not None
        ]
        if discharged_admissions:
            total_days = sum(
                (a.discharge_date - a.admission_date).days
                for a in discharged_admissions
            )
            avg_length_of_stay = total_days / len(discharged_admissions)

        return {
            "total_admissions": len(all_admissions),
            "active_admissions": len(active_admissions),
            "discharged_admissions": len(discharged_admissions),
            "average_length_of_stay_days": round(avg_length_of_stay, 2),
        }
