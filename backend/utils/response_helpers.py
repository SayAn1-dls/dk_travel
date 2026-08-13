"""
Standardized API response helpers for DK Travel backend.

Usage:
    from utils.response_helpers import success_response, error_response

    return success_response(data={"user": user}, message="Login successful")
    return error_response(message="Invalid credentials", status_code=401)
"""

from flask import jsonify


def success_response(data=None, message="Success", status_code=200):
    """Return a standardized success JSON response."""
    payload = {
        "success": True,
        "message": message,
        "data": data,
    }
    return jsonify(payload), status_code


def error_response(message="An error occurred", status_code=400, errors=None):
    """Return a standardized error JSON response."""
    payload = {
        "success": False,
        "message": message,
        "errors": errors,
    }
    return jsonify(payload), status_code


def paginated_response(data, page, per_page, total, message="Success"):
    """Return a standardized paginated JSON response."""
    payload = {
        "success": True,
        "message": message,
        "data": data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        },
    }
    return jsonify(payload), 200
