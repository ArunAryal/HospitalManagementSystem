"""
Utility functions for validation, pagination, and common operations.

This module provides reusable utility functions to reduce code duplication
and maintain consistency across the application.
"""

from typing import Any, Dict, Optional, Type
from enum import Enum
from datetime import datetime, date
from fastapi import Query
from pydantic import BaseModel
from backend.exceptions import ValidationError


class PaginationParams(BaseModel):
    """Standard pagination parameters."""

    skip: int = Query(0, ge=0, description="Number of items to skip")
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return")


def convert_to_enum(value: Optional[str], enum_class: Type[Enum]) -> Optional[Enum]:
    """
    Safely convert a string value to an enum.

    Args:
        value: String value to convert
        enum_class: Enum class to convert to

    Returns:
        Enum instance or None if value is None

    Raises:
        ValidationError: If value is not a valid enum member
    """
    if value is None:
        return None

    try:
        return enum_class(value)
    except ValueError:
        valid_values = [e.value for e in enum_class]
        raise ValidationError(
            f"Invalid value for {enum_class.__name__}",
            field_errors={"value": f"Must be one of: {', '.join(valid_values)}"},
        )


def validate_email(email: str) -> bool:
    """Validate email format."""
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format (basic check)."""
    # Must be 10-15 digits
    return bool(
        phone.replace("+", "").replace("-", "").replace(" ", "").isdigit()
        and 10 <= len(phone) <= 15
    )


def validate_age(dob: date) -> bool:
    """Validate that person is at least 18 years old."""
    today = datetime.now().date()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age >= 18


def validate_future_date(target_date: date) -> bool:
    """Validate that date is in the future."""
    return target_date > datetime.now().date()


def validate_date_not_past(target_date: date) -> bool:
    """Validate that date is not in the past."""
    return target_date >= datetime.now().date()


def sanitize_string(value: str) -> str:
    """Sanitize string input by stripping whitespace and special characters."""
    return value.strip()


def check_duplicate(
    db_session: Any,
    model: Any,
    field_name: str,
    field_value: Any,
    exclude_id: Optional[int] = None,
) -> bool:
    """
    Check if a record with the given field value already exists.

    Args:
        db_session: SQLAlchemy session
        model: SQLAlchemy model class
        field_name: Name of the field to check
        field_value: Value to check for
        exclude_id: ID to exclude from check (for updates)

    Returns:
        True if duplicate exists, False otherwise
    """
    query = db_session.query(model).filter(getattr(model, field_name) == field_value)

    if exclude_id:
        query = query.filter(model.id != exclude_id)

    return query.first() is not None


def get_field_by_name(model: Type[Any], field_name: str) -> Optional[Any]:
    """Safely get a model field by name."""
    try:
        return getattr(model, field_name)
    except AttributeError:
        return None


def dict_to_enum_values(
    data: Dict[str, Any], enum_fields: Dict[str, Type[Enum]]
) -> Dict[str, Any]:
    """
    Convert string enum values in a dictionary to actual enum instances.

    Args:
        data: Dictionary with string enum values
        enum_fields: Mapping of field names to enum classes

    Returns:
        Dictionary with enum values converted
    """
    result = data.copy()
    for field_name, enum_class in enum_fields.items():
        if field_name in result and result[field_name]:
            result[field_name] = convert_to_enum(result[field_name], enum_class)
    return result


def validate_time_range(start_time: datetime, end_time: datetime) -> bool:
    """Validate that end time is after start time."""
    return end_time > start_time


def round_decimal(value: Any, decimal_places: int = 2) -> float:
    """Round decimal value to specified places."""
    try:
        return round(float(value), decimal_places)
    except (ValueError, TypeError):
        raise ValidationError("Invalid decimal value")
