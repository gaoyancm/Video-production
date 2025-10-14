"""Schemas for tracking asynchronous jobs."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job lifecycle statuses."""

    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class JobInfo(BaseModel):
    """Job metadata shared with clients."""

    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(default=JobStatus.pending, description="Current job status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    detail: Optional[str] = Field(default=None, description="Optional status detail message")
    download_url: Optional[str] = Field(
        default=None,
        description="URL for downloading generated assets when job is complete",
    )
