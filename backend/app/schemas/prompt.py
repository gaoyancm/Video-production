"""Data models for prompt generation."""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class SubmissionTarget(str, Enum):
    """Available downstream systems for prompts."""

    llm = "llm"
    comfyui = "comfyui"
    both = "both"


class TextPromptRequest(BaseModel):
    """Request payload for text-only prompt generation."""

    text: str = Field(..., description="User provided text prompt or script")
    reference_style: Optional[str] = Field(
        default=None,
        description="Optional reference style or mood for the target video",
    )
    target_model: Optional[str] = Field(
        default=None,
        description="Specific model identifier to route prompt generation",
    )
    submit_to: SubmissionTarget = Field(
        default=SubmissionTarget.llm,
        description="Where to forward the generated prompt",
    )
    comfyui_endpoint: Optional[str] = Field(
        default=None, description="Override ComfyUI endpoint for this request"
    )


class PromptResponse(BaseModel):
    """Standard prompt response payload."""

    prompt: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
