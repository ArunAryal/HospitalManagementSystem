"""
Service layer for billing-related business logic.

This module implements the service layer for billing operations, separating
business logic from route handlers.
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session, selectinload

from backend import models, schemas
from backend.exceptions import (
    ResourceNotFoundError,
    ValidationError,
    InvalidOperationError,
)
from backend.logging_config import BusinessLogger


class BillingRepository:
    """Repository for billing data access."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, bill_data: schemas.BillCreate) -> models.Bill:
        """Create a new bill."""
        db_bill = models.Bill(**bill_data.model_dump())
        self.db.add(db_bill)
        self.db.commit()
        self.db.refresh(db_bill)
        return db_bill

    def get_by_id(self, bill_id: int) -> Optional[models.Bill]:
        """Get bill by ID with relationships."""
        return (
            self.db.query(models.Bill)
            .options(selectinload(models.Bill.patient))
            .filter(models.Bill.bill_id == bill_id)
            .first()
        )

    def list_all(self, skip: int = 0, limit: int = 100) -> List[models.Bill]:
        """List all bills."""
        return (
            self.db.query(models.Bill)
            .options(selectinload(models.Bill.patient))
            .order_by(models.Bill.bill_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_patient(
        self, patient_id: int, skip: int = 0, limit: int = 100
    ) -> List[models.Bill]:
        """Get bills for a patient."""
        return (
            self.db.query(models.Bill)
            .filter(models.Bill.patient_id == patient_id)
            .order_by(models.Bill.bill_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self, status: models.PaymentStatus, skip: int = 0, limit: int = 100
    ) -> List[models.Bill]:
        """Get bills by payment status."""
        return (
            self.db.query(models.Bill)
            .filter(models.Bill.payment_status == status)
            .order_by(models.Bill.bill_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, bill_id: int, update_data: schemas.BillUpdate) -> models.Bill:
        """Update bill."""
        bill = self.get_by_id(bill_id)
        if not bill:
            raise ResourceNotFoundError("Bill", bill_id)

        update_dict = update_data.model_dump(exclude_unset=True)

        # Convert string enums to enum instances
        if "payment_status" in update_dict and isinstance(
            update_dict["payment_status"], str
        ):
            update_dict["payment_status"] = models.PaymentStatus(
                update_dict["payment_status"]
            )
        if "payment_method" in update_dict and isinstance(
            update_dict["payment_method"], str
        ):
            update_dict["payment_method"] = models.PaymentMethod(
                update_dict["payment_method"]
            )

        for field, value in update_dict.items():
            if value is not None:
                setattr(bill, field, value)

        self.db.commit()
        self.db.refresh(bill)
        return bill

    def delete(self, bill_id: int) -> bool:
        """Delete bill."""
        bill = self.get_by_id(bill_id)
        if not bill:
            raise ResourceNotFoundError("Bill", bill_id)

        self.db.delete(bill)
        self.db.commit()
        return True

    def count_pending(self) -> int:
        """Get count of pending bills."""
        return (
            self.db.query(models.Bill)
            .filter(models.Bill.payment_status == models.PaymentStatus.Pending)
            .count()
        )

    def get_total_revenue(self, paid_only: bool = True) -> Decimal:
        """Get total revenue from bills."""
        query = self.db.query(models.Bill)
        if paid_only:
            query = query.filter(
                models.Bill.payment_status == models.PaymentStatus.Paid
            )

        result = query.with_entities(
            __import__("sqlalchemy").func.sum(models.Bill.paid_amount)
        ).scalar()

        return result or Decimal(0)


class BillingService:
    """Business logic service for billing operations."""

    def __init__(self, repository: BillingRepository, db: Session):
        self.repository = repository
        self.db = db
        self.logger = BusinessLogger()

    def create_bill(self, bill_data: schemas.BillCreate) -> schemas.Bill:
        """
        Create a new bill with validation.

        Validates:
        - Patient exists
        - Admission/Appointment exists (if provided)
        - Bill amount is positive
        """
        # Verify patient exists
        patient = (
            self.db.query(models.Patient)
            .filter(models.Patient.patient_id == bill_data.patient_id)
            .first()
        )
        if not patient:
            raise ResourceNotFoundError("Patient", bill_data.patient_id)

        # Verify admission if provided
        if bill_data.admission_id:
            admission = (
                self.db.query(models.Admission)
                .filter(models.Admission.admission_id == bill_data.admission_id)
                .first()
            )
            if not admission:
                raise ResourceNotFoundError("Admission", bill_data.admission_id)

        # Verify appointment if provided
        if bill_data.appointment_id:
            appointment = (
                self.db.query(models.Appointment)
                .filter(models.Appointment.appointment_id == bill_data.appointment_id)
                .first()
            )
            if not appointment:
                raise ResourceNotFoundError("Appointment", bill_data.appointment_id)

        # Validate bill amount
        if bill_data.total_amount <= 0:
            raise ValidationError(
                "Invalid bill amount",
                field_errors={"total_amount": "Total amount must be greater than 0"},
            )

        bill = self.repository.create(bill_data)
        self.logger.log_operation("Bill created", f"ID: {bill.bill_id}")

        return schemas.Bill.model_validate(bill)

    def get_bill(self, bill_id: int) -> schemas.Bill:
        """Get a single bill."""
        bill = self.repository.get_by_id(bill_id)
        if not bill:
            raise ResourceNotFoundError("Bill", bill_id)

        return schemas.Bill.model_validate(bill)

    def list_bills(self, skip: int = 0, limit: int = 100) -> List[schemas.Bill]:
        """List all bills."""
        bills = self.repository.list_all(skip=skip, limit=limit)
        return [schemas.Bill.model_validate(b) for b in bills]

    def get_patient_bills(
        self, patient_id: int, skip: int = 0, limit: int = 100
    ) -> List[schemas.Bill]:
        """Get bills for a patient."""
        # Verify patient exists
        patient = (
            self.db.query(models.Patient)
            .filter(models.Patient.patient_id == patient_id)
            .first()
        )
        if not patient:
            raise ResourceNotFoundError("Patient", patient_id)

        bills = self.repository.get_by_patient(patient_id, skip=skip, limit=limit)
        return [schemas.Bill.model_validate(b) for b in bills]

    def update_bill(
        self, bill_id: int, update_data: schemas.BillUpdate
    ) -> schemas.Bill:
        """Update an existing bill."""
        # Verify bill exists
        _ = self.repository.get_by_id(bill_id)
        if not _:
            raise ResourceNotFoundError("Bill", bill_id)

        bill = self.repository.update(bill_id, update_data)
        self.logger.log_operation("Bill updated", f"ID: {bill_id}")

        return schemas.Bill.model_validate(bill)

    def record_payment(
        self, bill_id: int, amount: Decimal, payment_method: str
    ) -> schemas.Bill:
        """Record a payment for a bill."""
        bill = self.repository.get_by_id(bill_id)
        if not bill:
            raise ResourceNotFoundError("Bill", bill_id)

        if amount <= 0:
            raise ValidationError(
                "Invalid payment amount",
                field_errors={"amount": "Payment amount must be greater than 0"},
            )

        remaining = bill.total_amount - bill.paid_amount
        if amount > remaining:
            raise InvalidOperationError(
                f"Payment amount exceeds remaining balance (${remaining})"
            )

        # Update bill
        bill.paid_amount += amount
        bill.payment_method = models.PaymentMethod(payment_method)

        # Update payment status
        if bill.paid_amount >= bill.total_amount:
            bill.payment_status = models.PaymentStatus.Paid
        elif bill.paid_amount > 0:
            bill.payment_status = models.PaymentStatus.PartiallyPaid
        else:
            bill.payment_status = models.PaymentStatus.Pending

        self.db.commit()
        self.db.refresh(bill)

        self.logger.log_operation(
            "Payment recorded",
            f"Bill ID: {bill_id}, Amount: ${amount}, Status: {bill.payment_status.value}",
        )

        return schemas.Bill.model_validate(bill)

    def delete_bill(self, bill_id: int) -> bool:
        """Delete a bill."""
        result = self.repository.delete(bill_id)
        if result:
            self.logger.log_operation("Bill deleted", f"ID: {bill_id}")
        return result

    def get_billing_stats(self) -> Dict[str, Any]:
        """Get billing statistics."""
        total_bills = self.db.query(models.Bill).count()
        pending_bills = self.repository.count_pending()
        total_revenue = self.repository.get_total_revenue(paid_only=True)

        return {
            "total_bills": total_bills,
            "pending_bills": pending_bills,
            "total_revenue": float(total_revenue),
        }

    def generate_discharge_bill(self, admission_id: int) -> Optional[schemas.Bill]:
        """
        Generate or update a bill when a patient is discharged.
        
        Calculates:
        - Room charges: room.charge_per_day × number of nights
        - All medicine charges from prescriptions
        - Consultation fee (if not already billed through appointment)
        
        Returns:
        - Updated bill if successful, None if no charges to add
        """
        # Get admission details
        admission = (
            self.db.query(models.Admission)
            .filter(models.Admission.admission_id == admission_id)
            .first()
        )
        if not admission:
            raise ResourceNotFoundError("Admission", admission_id)

        if admission.discharge_date is None:
            raise InvalidOperationError("Admission is not discharged yet")

        # Calculate length of stay
        length_of_stay = (admission.discharge_date - admission.admission_date).days
        if length_of_stay == 0:
            length_of_stay = 1  # Minimum 1 day charge

        # Get room charges
        room = (
            self.db.query(models.Room)
            .filter(models.Room.room_id == admission.room_id)
            .first()
        )
        if not room:
            raise ResourceNotFoundError("Room", admission.room_id)

        room_charges = Decimal(str(room.charge_per_day)) * Decimal(str(length_of_stay))

        # Get medicine charges from prescriptions associated with this admission
        prescriptions = (
            self.db.query(models.Prescription)
            .join(models.MedicalRecord)
            .filter(models.MedicalRecord.patient_id == admission.patient_id)
            .all()
        )

        medicine_charges = Decimal(0)
        for prescription in prescriptions:
            medicine = (
                self.db.query(models.Medicine)
                .filter(models.Medicine.medicine_id == prescription.medicine_id)
                .first()
            )
            if medicine:
                medicine_charges += Decimal(str(medicine.unit_price)) * Decimal(
                    str(prescription.quantity)
                )

        # Check if bill exists for this admission
        existing_bill = (
            self.db.query(models.Bill)
            .filter(models.Bill.admission_id == admission_id)
            .first()
        )

        if existing_bill:
            # Update existing bill
            existing_bill.room_charges = room_charges
            existing_bill.medicine_charges = medicine_charges
            existing_bill.total_amount = (
                existing_bill.consultation_fee
                + medicine_charges
                + room_charges
                + existing_bill.other_charges
            )
            self.db.commit()
            self.db.refresh(existing_bill)

            self.logger.log_operation(
                "Discharge bill updated",
                f"Admission ID: {admission_id}, Total: ${existing_bill.total_amount}",
            )

            return schemas.Bill.model_validate(existing_bill)
        else:
            # Create new bill for admission with discharge
            total_amount = room_charges + medicine_charges
            if total_amount <= 0:
                total_amount = Decimal("0.01")  # Minimum charge

            new_bill = models.Bill(
                patient_id=admission.patient_id,
                admission_id=admission_id,
                consultation_fee=Decimal(0),
                medicine_charges=medicine_charges,
                room_charges=room_charges,
                other_charges=Decimal(0),
                total_amount=total_amount,
                payment_status=models.PaymentStatus.Pending,
            )
            self.db.add(new_bill)
            self.db.commit()
            self.db.refresh(new_bill)

            self.logger.log_operation(
                "Discharge bill created",
                f"Admission ID: {admission_id}, Total: ${new_bill.total_amount}",
            )

            return schemas.Bill.model_validate(new_bill)

    def add_medicine_charges_to_bill(
        self, medical_record_id: int, medicine_id: int, quantity: int
    ) -> Optional[schemas.Bill]:
        """
        Update patient's bill with medicine charges when a prescription is added.
        
        This method:
        - Finds or creates a bill for the patient
        - Adds the medicine charges to the bill
        - Updates the total amount
        
        Returns:
        - Updated/created bill
        """
        # Get medical record and patient
        medical_record = (
            self.db.query(models.MedicalRecord)
            .filter(models.MedicalRecord.record_id == medical_record_id)
            .first()
        )
        if not medical_record:
            raise ResourceNotFoundError("MedicalRecord", medical_record_id)

        patient_id = medical_record.patient_id

        # Get medicine details
        medicine = (
            self.db.query(models.Medicine)
            .filter(models.Medicine.medicine_id == medicine_id)
            .first()
        )
        if not medicine:
            raise ResourceNotFoundError("Medicine", medicine_id)

        medicine_charge = Decimal(str(medicine.unit_price)) * Decimal(str(quantity))

        # Try to find existing bill for this patient and medical record's appointment
        existing_bill = None
        if medical_record.appointment_id:
            existing_bill = (
                self.db.query(models.Bill)
                .filter(
                    models.Bill.patient_id == patient_id,
                    models.Bill.appointment_id == medical_record.appointment_id,
                )
                .first()
            )

        # If no appointment bill, check for admission bill
        if not existing_bill:
            admission = (
                self.db.query(models.Admission)
                .filter(
                    models.Admission.patient_id == patient_id,
                    models.Admission.discharge_date.is_(None),
                )
                .first()
            )
            if admission:
                existing_bill = (
                    self.db.query(models.Bill)
                    .filter(models.Bill.admission_id == admission.admission_id)
                    .first()
                )

        if existing_bill:
            # Update existing bill
            existing_bill.medicine_charges += medicine_charge
            existing_bill.total_amount = (
                existing_bill.consultation_fee
                + existing_bill.medicine_charges
                + existing_bill.room_charges
                + existing_bill.other_charges
            )
            self.db.commit()
            self.db.refresh(existing_bill)

            self.logger.log_operation(
                "Medicine charges added to bill",
                f"Bill ID: {existing_bill.bill_id}, Medicine: ${medicine_charge}, Total: ${existing_bill.total_amount}",
            )

            return schemas.Bill.model_validate(existing_bill)
        else:
            # Create new bill with medicine charges
            new_bill = models.Bill(
                patient_id=patient_id,
                appointment_id=medical_record.appointment_id,
                consultation_fee=Decimal(0),
                medicine_charges=medicine_charge,
                room_charges=Decimal(0),
                other_charges=Decimal(0),
                total_amount=medicine_charge,
                payment_status=models.PaymentStatus.Pending,
            )
            self.db.add(new_bill)
            self.db.commit()
            self.db.refresh(new_bill)

            self.logger.log_operation(
                "Medicine bill created",
                f"Patient ID: {patient_id}, Medicine: ${medicine_charge}",
            )

            return schemas.Bill.model_validate(new_bill)
