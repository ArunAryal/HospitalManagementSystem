"""
Base repository and service classes for data access and business logic separation.

This module provides abstract base classes for implementing the repository pattern,
enabling clean separation between data access layers and business logic.
"""

from typing import TypeVar, Generic, List, Type, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.exceptions import ResourceNotFoundError

T = TypeVar("T")  # Generic type for model


class BaseRepository(Generic[T]):
    """
    Abstract base repository for CRUD operations.

    Implementations should inherit from this class to provide consistent
    data access patterns across the application.
    """

    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def create(self, obj_in: Any, commit: bool = True) -> T:
        """Create a new record."""
        db_obj = self.model(**obj_in.model_dump())
        self.db.add(db_obj)
        if commit:
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def get_by_id(self, id: Any) -> Optional[T]:
        """Retrieve a record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        desc_order: bool = False,
    ) -> List[T]:
        """Retrieve records with pagination and optional ordering."""
        query = self.db.query(self.model).offset(skip).limit(limit)

        if order_by:
            column = getattr(self.model, order_by, None)
            if column:
                query = query.order_by(desc(column) if desc_order else column)

        return query.all()

    def update(self, id: Any, obj_in: Dict[str, Any], commit: bool = True) -> T:
        """Update an existing record."""
        db_obj = self.get_by_id(id)
        if not db_obj:
            raise ResourceNotFoundError(self.model.__name__, id)

        for field, value in obj_in.items():
            if value is not None:
                setattr(db_obj, field, value)

        if commit:
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: Any, commit: bool = True) -> bool:
        """Delete a record by ID."""
        db_obj = self.get_by_id(id)
        if not db_obj:
            raise ResourceNotFoundError(self.model.__name__, id)

        self.db.delete(db_obj)
        if commit:
            self.db.commit()
        return True

    def exists(self, **filters) -> bool:
        """Check if a record exists with given filters."""
        return self.db.query(self.model).filter_by(**filters).first() is not None

    def get_by_filter(self, **filters) -> Optional[T]:
        """Get a single record by filters."""
        return self.db.query(self.model).filter_by(**filters).first()

    def filter_by(self, skip: int = 0, limit: int = 100, **filters) -> List[T]:
        """Get records filtered by given criteria."""
        return (
            self.db.query(self.model)
            .filter_by(**filters)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count(self, **filters) -> int:
        """Count records matching the filters."""
        query = self.db.query(self.model)
        if filters:
            query = query.filter_by(**filters)
        return query.count()


class BaseService(Generic[T]):
    """
    Abstract base service for business logic.

    Services should contain the core business logic and delegate
    data access to repository instances.
    """

    def __init__(self, repository: BaseRepository[T]):
        self.repository = repository
        self.model_name = repository.model.__name__

    def create_item(self, item_data: Any) -> T:
        """Create a new item."""
        return self.repository.create(item_data)

    def get_item(self, item_id: Any) -> T:
        """Get a single item by ID."""
        item = self.repository.get_by_id(item_id)
        if not item:
            raise ResourceNotFoundError(self.model_name, item_id)
        return item

    def list_items(self, skip: int = 0, limit: int = 100) -> List[T]:
        """List all items with pagination."""
        return self.repository.get_all(skip=skip, limit=limit)

    def update_item(self, item_id: Any, item_update: Dict[str, Any]) -> T:
        """Update an existing item."""
        return self.repository.update(item_id, item_update)

    def delete_item(self, item_id: Any) -> bool:
        """Delete an item."""
        return self.repository.delete(item_id)

    def item_exists(self, **filters) -> bool:
        """Check if an item exists."""
        return self.repository.exists(**filters)
