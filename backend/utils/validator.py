"""Input validation helpers for Wanderly."""

import re
from datetime import datetime, date
from typing import Optional, Tuple

from fastapi import HTTPException


def validate_date(date_str: str, field_name: str = "date") -> date:
    """Validate and parse a date string.

    Args:
        date_str: Date in YYYY-MM-DD format
        field_name: Name of the field for error messages

    Returns:
        Parsed date object

    Raises:
        HTTPException: If date format is invalid
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name} format. Expected YYYY-MM-DD, got '{date_str}'"
        )


def validate_date_range(
    start_date: str, end_date: str
) -> Tuple[date, date]:
    """Validate a date range (start must be before end).

    Returns:
        Tuple of (start_date, end_date)
    """
    start = validate_date(start_date, "start_date")
    end = validate_date(end_date, "end_date")

    if start >= end:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before end_date"
        )

    return start, end


def validate_email(email: str) -> str:
    """Validate an email address format.

    Returns:
        The email if valid

    Raises:
        HTTPException: If email format is invalid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid email format: '{email}'"
        )
    return email.lower().strip()


def validate_pagination(
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100,
) -> Tuple[int, int]:
    """Validate pagination parameters.

    Returns:
        Tuple of (page, page_size) with valid values
    """
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 1
    if page_size > max_page_size:
        page_size = max_page_size

    return page, page_size


def validate_rating(rating: int, field_name: str = "rating") -> int:
    """Validate a star rating (1-5)."""
    if not 1 <= rating <= 5:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be between 1 and 5, got {rating}"
        )
    return rating


def validate_sort_order(order: str) -> str:
    """Validate sort order parameter."""
    order = order.lower().strip()
    if order not in ("asc", "desc"):
        raise HTTPException(
            status_code=400,
            detail=f"sort_order must be 'asc' or 'desc', got '{order}'"
        )
    return order


def validate_currency(currency: str) -> str:
    """Validate a currency code (3-letter ISO 4217)."""
    currency = currency.upper().strip()
    if not re.match(r'^[A-Z]{3}$', currency):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid currency code: '{currency}'. Expected 3-letter ISO 4217 code."
        )
    return currency


def sanitize_string(value: str, max_length: int = 500) -> str:
    """Sanitize a string input by stripping whitespace and limiting length."""
    return value.strip()[:max_length]


def validate_object_id(id_str: str, field_name: str = "id") -> str:
    """Validate a MongoDB ObjectId format."""
    if not re.match(r'^[0-9a-fA-F]{24}$', id_str):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name} format: '{id_str}'"
        )
    return id_str
