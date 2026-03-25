from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import schemas
from backend.services import BillingService, BillingRepository
from backend.exceptions import APIException

router = APIRouter(prefix="/bills", tags=["Billing"])


def get_billing_service(db: Session = Depends(get_db)) -> BillingService:
    """Dependency injection for BillingService."""
    return BillingService(BillingRepository(db), db)


@router.get("/", response_model=List[schemas.Bill])
def list_bills(
    patient_id: Optional[int] = None,
    payment_status: Optional[str] = Query(
        None, pattern="^(Pending|Paid|Partially Paid)$"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: BillingService = Depends(get_billing_service),
):
    """List all bills."""
    try:
        if patient_id:
            return service.get_patient_bills(patient_id, skip=skip, limit=limit)
        return service.list_bills(skip=skip, limit=limit)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/", response_model=schemas.Bill, status_code=201)
def create_bill(
    bill: schemas.BillCreate,
    service: BillingService = Depends(get_billing_service),
):
    """Create a new bill."""
    try:
        return service.create_bill(bill)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/{bill_id}", response_model=schemas.Bill)
def get_bill(
    bill_id: int,
    service: BillingService = Depends(get_billing_service),
):
    """Get a single bill."""
    try:
        return service.get_bill(bill_id)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put("/{bill_id}", response_model=schemas.Bill)
def update_bill(
    bill_id: int,
    update: schemas.BillUpdate,
    service: BillingService = Depends(get_billing_service),
):
    """Update a bill."""
    try:
        return service.update_bill(bill_id, update)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/{bill_id}/payment", response_model=schemas.Bill)
def record_payment(
    bill_id: int,
    amount: Decimal,
    payment_method: str,
    service: BillingService = Depends(get_billing_service),
):
    """Record a payment for a bill."""
    try:
        return service.record_payment(bill_id, amount, payment_method)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete("/{bill_id}", status_code=204)
def delete_bill(
    bill_id: int,
    service: BillingService = Depends(get_billing_service),
):
    """Delete a bill."""
    try:
        service.delete_bill(bill_id)
        return None
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post(
    "/admission/{admission_id}/generate", response_model=schemas.Bill, status_code=201
)
def generate_bill_for_admission(
    admission_id: int,
    service: BillingService = Depends(get_billing_service),
):
    """Generate or get auto-calculated bill for an admission."""
    try:
        return service.create_bill(
            schemas.BillCreate(
                patient_id=0,  # Will be filled by service
                admission_id=admission_id,
                total_amount=0,  # Will be calculated by service
            )
        )
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/stats/billing", response_model=dict)
def get_billing_stats(
    service: BillingService = Depends(get_billing_service),
):
    """Get billing statistics."""
    try:
        return service.get_billing_stats()
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
