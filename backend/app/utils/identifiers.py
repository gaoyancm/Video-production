"""Helper utilities for ID generation."""

import uuid


def new_job_id(prefix: str = "job") -> str:
    """Return a URL-safe job identifier."""
    return f"{prefix}_{uuid.uuid4().hex}"
