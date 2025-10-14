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

    text: str = Field(..., description="【文本输入】用户提供的脚本或描述内容")
    reference_style: Optional[str] = Field(
        default=None,
        description="【文本输入】可选的参考风格或情绪标签",
    )
    target_model: Optional[str] = Field(
        default=None,
        description="【文本输入】指定大模型标识（如 gpt-4o-mini、qwen-plus 等）",
    )
    submit_to: SubmissionTarget = Field(
        default=SubmissionTarget.llm,
        description="Where to forward the generated prompt",
    )
    comfyui_endpoint: Optional[str] = Field(
        default=None, description="【文本输入】本次请求使用的 ComfyUI 服务器地址"
    )


class PromptResponse(BaseModel):
    """Standard prompt response payload."""

    prompt: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
