from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import schemas
from backend.services import MedicineService, MedicineRepository
from backend.exceptions import APIException

router = APIRouter(prefix="/medicines", tags=["Medicines"])


def get_medicine_service(db: Session = Depends(get_db)) -> MedicineService:
    """Dependency injection for MedicineService."""
    return MedicineService(MedicineRepository(db))


@router.get("/", response_model=List[schemas.Medicine])
def list_medicines(
    search: Optional[str] = Query(None, description="Search by name or manufacturer"),
    low_stock: bool = Query(
        False, description="Filter medicines at or below reorder level"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: MedicineService = Depends(get_medicine_service),
):
    """List all medicines."""
    try:
        if search:
            return service.search_medicines(search, skip=skip, limit=limit)
        if low_stock:
            return service.get_low_stock_medicines(skip=skip, limit=limit)
        return service.list_medicines(skip=skip, limit=limit)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/", response_model=schemas.Medicine, status_code=201)
def create_medicine(
    medicine: schemas.MedicineCreate,
    service: MedicineService = Depends(get_medicine_service),
):
    """Create a new medicine."""
    try:
        return service.create_medicine(medicine)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/low-stock", response_model=List[schemas.Medicine])
def get_low_stock_medicines(
    service: MedicineService = Depends(get_medicine_service),
):
    """Get medicines with low stock."""
    try:
        return service.get_low_stock_medicines(skip=0, limit=999999)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/{medicine_id}", response_model=schemas.Medicine)
def get_medicine(
    medicine_id: int,
    service: MedicineService = Depends(get_medicine_service),
):
    """Get a single medicine."""
    try:
        return service.get_medicine(medicine_id)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put("/{medicine_id}", response_model=schemas.Medicine)
def update_medicine(
    medicine_id: int,
    update: schemas.MedicineUpdate,
    service: MedicineService = Depends(get_medicine_service),
):
    """Update a medicine."""
    try:
        return service.update_medicine(medicine_id, update)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.patch("/{medicine_id}/restock", response_model=schemas.Medicine)
def restock_medicine(
    medicine_id: int,
    quantity: int = Query(..., gt=0, description="Units to add to stock"),
    service: MedicineService = Depends(get_medicine_service),
):
    """Add medicine to stock."""
    try:
        return service.restock_medicine(medicine_id, quantity)
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete("/{medicine_id}", status_code=204)
def delete_medicine(
    medicine_id: int,
    service: MedicineService = Depends(get_medicine_service),
):
    """Delete a medicine."""
    try:
        service.delete_medicine(medicine_id)
        return None
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/stats/inventory", response_model=dict)
def get_inventory_stats(
    service: MedicineService = Depends(get_medicine_service),
):
    """Get inventory statistics."""
    try:
        return service.get_inventory_stats()
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
