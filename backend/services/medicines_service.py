"""
Service layer for medicine-related business logic.

This module implements the service layer for medicine operations, separating
business logic from route handlers.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.exceptions import (
    DuplicateResourceError,
    ResourceNotFoundError,
    ValidationError,
    InvalidOperationError,
)
from backend.logging_config import BusinessLogger


class MedicineRepository:
    """Repository for medicine data access."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, medicine_data: schemas.MedicineCreate) -> models.Medicine:
        """Create a new medicine."""
        db_medicine = models.Medicine(**medicine_data.model_dump())
        self.db.add(db_medicine)
        self.db.commit()
        self.db.refresh(db_medicine)
        return db_medicine

    def get_by_id(self, medicine_id: int) -> Optional[models.Medicine]:
        """Get medicine by ID."""
        return (
            self.db.query(models.Medicine)
            .filter(models.Medicine.medicine_id == medicine_id)
            .first()
        )

    def get_by_name(self, name: str) -> Optional[models.Medicine]:
        """Get medicine by name."""
        return (
            self.db.query(models.Medicine)
            .filter(models.Medicine.medicine_name == name)
            .first()
        )

    def list_all(self, skip: int = 0, limit: int = 100) -> List[models.Medicine]:
        """List all medicines."""
        return (
            self.db.query(models.Medicine)
            .order_by(models.Medicine.medicine_name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search(
        self, query: str, skip: int = 0, limit: int = 100
    ) -> List[models.Medicine]:
        """Search medicines by name or manufacturer."""
        like_pattern = f"%{query}%"
        return (
            self.db.query(models.Medicine)
            .filter(
                (models.Medicine.medicine_name.ilike(like_pattern))
                | (models.Medicine.manufacturer.ilike(like_pattern))
            )
            .order_by(models.Medicine.medicine_name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_low_stock(self, skip: int = 0, limit: int = 100) -> List[models.Medicine]:
        """Get medicines with low stock."""
        return (
            self.db.query(models.Medicine)
            .filter(models.Medicine.stock_quantity <= models.Medicine.reorder_level)
            .order_by(models.Medicine.stock_quantity)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self, medicine_id: int, update_data: schemas.MedicineUpdate
    ) -> models.Medicine:
        """Update medicine."""
        medicine = self.get_by_id(medicine_id)
        if not medicine:
            raise ResourceNotFoundError("Medicine", medicine_id)

        for field, value in update_data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(medicine, field, value)

        self.db.commit()
        self.db.refresh(medicine)
        return medicine

    def update_stock(self, medicine_id: int, quantity: int) -> models.Medicine:
        """Update medicine stock."""
        medicine = self.get_by_id(medicine_id)
        if not medicine:
            raise ResourceNotFoundError("Medicine", medicine_id)

        medicine.stock_quantity += quantity
        self.db.commit()
        self.db.refresh(medicine)
        return medicine

    def delete(self, medicine_id: int) -> bool:
        """Delete medicine."""
        medicine = self.get_by_id(medicine_id)
        if not medicine:
            raise ResourceNotFoundError("Medicine", medicine_id)

        self.db.delete(medicine)
        self.db.commit()
        return True

    def count(self) -> int:
        """Get total medicine count."""
        return self.db.query(models.Medicine).count()


class MedicineService:
    """Business logic service for medicine operations."""

    def __init__(self, repository: MedicineRepository):
        self.repository = repository
        self.logger = BusinessLogger()

    def create_medicine(
        self, medicine_data: schemas.MedicineCreate
    ) -> schemas.Medicine:
        """
        Create a new medicine with validation.

        Validates:
        - Medicine name is unique
        - Unit price is positive
        - Stock quantity is valid
        """
        # Check for duplicate
        existing = self.repository.get_by_name(medicine_data.medicine_name)
        if existing:
            self.logger.log_duplicate_detection("Medicine", "name")
            raise DuplicateResourceError(
                "Medicine", "name", medicine_data.medicine_name
            )

        # Validate unit price
        if medicine_data.unit_price <= 0:
            raise ValidationError(
                "Invalid unit price",
                field_errors={"unit_price": "Unit price must be greater than 0"},
            )

        # Validate stock quantity
        if medicine_data.stock_quantity < 0:
            raise ValidationError(
                "Invalid stock quantity",
                field_errors={"stock_quantity": "Stock quantity cannot be negative"},
            )

        medicine = self.repository.create(medicine_data)
        self.logger.log_operation("Medicine created", f"ID: {medicine.medicine_id}")

        return schemas.Medicine.model_validate(medicine)

    def get_medicine(self, medicine_id: int) -> schemas.Medicine:
        """Get a single medicine."""
        medicine = self.repository.get_by_id(medicine_id)
        if not medicine:
            raise ResourceNotFoundError("Medicine", medicine_id)

        return schemas.Medicine.model_validate(medicine)

    def list_medicines(self, skip: int = 0, limit: int = 100) -> List[schemas.Medicine]:
        """List all medicines."""
        medicines = self.repository.list_all(skip=skip, limit=limit)
        return [schemas.Medicine.model_validate(m) for m in medicines]

    def search_medicines(
        self, query: str, skip: int = 0, limit: int = 100
    ) -> List[schemas.Medicine]:
        """Search medicines."""
        if not query or len(query) < 2:
            raise ValidationError("Search query must be at least 2 characters")

        medicines = self.repository.search(query, skip=skip, limit=limit)
        return [schemas.Medicine.model_validate(m) for m in medicines]

    def get_low_stock_medicines(
        self, skip: int = 0, limit: int = 100
    ) -> List[schemas.Medicine]:
        """Get medicines with low stock."""
        medicines = self.repository.get_low_stock(skip=skip, limit=limit)
        return [schemas.Medicine.model_validate(m) for m in medicines]

    def update_medicine(
        self, medicine_id: int, update_data: schemas.MedicineUpdate
    ) -> schemas.Medicine:
        """Update an existing medicine."""
        # Verify medicine exists
        _ = self.repository.get_by_id(medicine_id)
        if not _:
            raise ResourceNotFoundError("Medicine", medicine_id)

        # Validate unit price if provided
        if update_data.unit_price is not None and update_data.unit_price <= 0:
            raise ValidationError(
                "Invalid unit price",
                field_errors={"unit_price": "Unit price must be greater than 0"},
            )

        # Validate stock quantity if provided
        if update_data.stock_quantity is not None and update_data.stock_quantity < 0:
            raise ValidationError(
                "Invalid stock quantity",
                field_errors={"stock_quantity": "Stock quantity cannot be negative"},
            )

        medicine = self.repository.update(medicine_id, update_data)
        self.logger.log_operation("Medicine updated", f"ID: {medicine_id}")

        return schemas.Medicine.model_validate(medicine)

    def restock_medicine(self, medicine_id: int, quantity: int) -> schemas.Medicine:
        """Add medicine to stock."""
        if quantity <= 0:
            raise ValidationError(
                "Invalid quantity",
                field_errors={"quantity": "Quantity must be greater than 0"},
            )

        medicine = self.repository.update_stock(medicine_id, quantity)
        self.logger.log_operation(
            "Medicine restocked", f"ID: {medicine_id}, Quantity: {quantity}"
        )

        return schemas.Medicine.model_validate(medicine)

    def remove_medicine_stock(
        self, medicine_id: int, quantity: int
    ) -> schemas.Medicine:
        """Remove medicine from stock (e.g., used for prescriptions)."""
        medicine = self.repository.get_by_id(medicine_id)
        if not medicine:
            raise ResourceNotFoundError("Medicine", medicine_id)

        if quantity <= 0:
            raise ValidationError(
                "Invalid quantity",
                field_errors={"quantity": "Quantity must be greater than 0"},
            )

        if medicine.stock_quantity < quantity:
            raise InvalidOperationError(
                f"Insufficient stock. Available: {medicine.stock_quantity}, Requested: {quantity}"
            )

        medicine = self.repository.update_stock(medicine_id, -quantity)
        self.logger.log_operation(
            "Medicine stock reduced", f"ID: {medicine_id}, Quantity: {quantity}"
        )

        return schemas.Medicine.model_validate(medicine)

    def delete_medicine(self, medicine_id: int) -> bool:
        """Delete a medicine."""
        result = self.repository.delete(medicine_id)
        if result:
            self.logger.log_operation("Medicine deleted", f"ID: {medicine_id}")
        return result

    def get_inventory_stats(self) -> Dict[str, Any]:
        """Get inventory statistics."""
        all_medicines = self.repository.list_all(skip=0, limit=999999)  # Get all
        low_stock = self.repository.get_low_stock(skip=0, limit=999999)

        total_value = sum(float(m.unit_price * m.stock_quantity) for m in all_medicines)

        return {
            "total_medicines": self.repository.count(),
            "total_stock_items": sum(m.stock_quantity for m in all_medicines),
            "low_stock_count": len(low_stock),
            "total_inventory_value": total_value,
        }
