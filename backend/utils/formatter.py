"""Response formatting utilities for Wanderly."""

from datetime import datetime
from typing import Any, Dict, List, Optional


def format_response(
    data: Any,
    message: str = "Success",
    status: str = "success",
    meta: Optional[Dict] = None,
) -> Dict:
    """Format a standard API response.

    Args:
        data: Response payload
        message: Human-readable message
        status: Response status (success/error)
        meta: Optional metadata (pagination, etc.)

    Returns:
        Formatted response dictionary
    """
    response = {
        "status": status,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    if meta:
        response["meta"] = meta
    return response


def format_error(
    message: str,
    code: str = "UNKNOWN_ERROR",
    details: Optional[Any] = None,
) -> Dict:
    """Format a standard error response.

    Args:
        message: Error message
        code: Error code for programmatic handling
        details: Additional error details

    Returns:
        Formatted error dictionary
    """
    response = {
        "status": "error",
        "error": {
            "code": code,
            "message": message,
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    if details:
        response["error"]["details"] = details
    return response


def format_pagination(
    total: int,
    page: int,
    page_size: int,
) -> Dict:
    """Format pagination metadata."""
    total_pages = max(1, (total + page_size - 1) // page_size)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


def format_price(
    amount: float,
    currency: str = "USD",
    locale: str = "en",
) -> str:
    """Format a price amount with currency symbol.

    Args:
        amount: Numeric amount
        currency: Currency code
        locale: Locale for formatting

    Returns:
        Formatted price string
    """
    symbols = {
        "USD": "$", "EUR": "\u20ac", "GBP": "\u00a3", "INR": "\u20b9",
        "JPY": "\u00a5", "CNY": "\u00a5", "KRW": "\u20a9",
        "AED": "AED ", "THB": "\u0e3f", "BRL": "R$",
    }
    symbol = symbols.get(currency, f"{currency} ")

    if currency in ("JPY", "KRW"):
        return f"{symbol}{int(amount):,}"
    return f"{symbol}{amount:,.2f}"


def format_duration(minutes: int) -> str:
    """Format a duration in minutes to a human-readable string."""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    remaining = minutes % 60
    if remaining == 0:
        return f"{hours}h"
    return f"{hours}h {remaining}m"


def format_distance(km: float) -> str:
    """Format a distance in kilometers."""
    if km < 1:
        return f"{int(km * 1000)}m"
    return f"{km:.1f} km"


def format_date_range(start: str, end: str) -> str:
    """Format a date range for display."""
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")
        delta = (end_dt - start_dt).days

        if start_dt.month == end_dt.month and start_dt.year == end_dt.year:
            return f"{start_dt.strftime('%b %d')}-{end_dt.strftime('%d, %Y')} ({delta} nights)"
        return f"{start_dt.strftime('%b %d')} - {end_dt.strftime('%b %d, %Y')} ({delta} nights)"
    except ValueError:
        return f"{start} to {end}"


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)].rsplit(" ", 1)[0] + suffix
