"""Schemas for media handling."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MediaProcessingMode(str, Enum):
    """Processing strategies for uploaded media."""

    direct = "direct"
    comfy = "comfy"


class MediaUploadResponse(BaseModel):
    """Response payload after persisting an upload."""

    job_id: str = Field(..., description="Tracking identifier for downstream processes")
    filename: str = Field(..., description="Original file name")
    mode: MediaProcessingMode = Field(default=MediaProcessingMode.direct)
    comfyui_endpoint: Optional[str] = Field(default=None, description="ComfyUI endpoint used for this job")
    detail: str = Field(default="Stored", description="Additional status detail")
