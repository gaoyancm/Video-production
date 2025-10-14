"""Application configuration powered by environment variables."""

from functools import lru_cache
from typing import Any, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Central application settings."""

    app_name: str = Field(default="Video Production API", description="Human friendly app name")
    api_v1_prefix: str = Field(default="/api/v1", description="Prefix for versioned API routes")
    debug: bool = Field(default=False, description="Enable debug mode")
    cors_origins: List[str] = Field(default_factory=lambda: ["*"], description="Allowed CORS origins")

    storage_dir: str = Field(default="storage", description="Local directory for temporary file storage")

    comfyui_base_url: Optional[str] = Field(default=None, description="Base URL for ComfyUI server (optional fallback)")
    dashscope_api_key: Optional[str] = Field(default=None, description="API key for DashScope/Tongyi-Qianwen")
    dashscope_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="DashScope compatible OpenAI API base URL",
    )
    openai_api_key: Optional[str] = Field(default=None, description="API key for OpenAI or compatible endpoints")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API base URL",
    )
    gemini_api_key: Optional[str] = Field(default=None, description="API key for Google Gemini")
    gemini_api_base_url: str = Field(
        default="https://generativelanguage.googleapis.com/v1beta",
        description="Base URL for Gemini Generative Language API",
    )
    default_openai_model: str = Field(
        default="gpt-4o-mini",
        description="Default OpenAI compatible model when target_model not provided",
    )
    default_dashscope_model: str = Field(
        default="qwen-plus",
        description="Default DashScope model when target_model not provided",
    )
    default_gemini_model: str = Field(
        default="gemini-1.5-flash",
        description="Default Gemini model when target_model not provided",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> List[str]:
        """允许逗号分隔的字符串或 JSON 列表."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return cached application settings."""
    return AppSettings()
