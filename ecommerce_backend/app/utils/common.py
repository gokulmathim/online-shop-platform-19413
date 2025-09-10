from typing import Any, Dict, Tuple
from flask import request


# PUBLIC_INTERFACE
def get_pagination_params(default_page: int = 1, default_page_size: int = 20) -> Tuple[int, int]:
    """Parse pagination params from request args."""
    try:
        page = int(request.args.get("page", default_page))
    except ValueError:
        page = default_page
    try:
        page_size = int(request.args.get("page_size", default_page_size))
    except ValueError:
        page_size = default_page_size
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    return page, page_size


# PUBLIC_INTERFACE
def error_response(message: str, status_code: int = 400, **extra: Any) -> Tuple[Dict[str, Any], int]:
    """Standardize error response format."""
    payload = {"message": message}
    if extra:
        payload["details"] = extra
    return payload, status_code
