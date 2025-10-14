"""FastAPI application entrypoint."""

from pathlib import Path

from fastapi import FastAPI

from .api.v1.router import api_router
from .core.config import get_settings
from .core.cors import setup_cors
from .core.logging import configure_logging

settings = get_settings()

configure_logging()

app = FastAPI(
    title="视频生成服务 API",
    description="用于将用户提供的素材转化为视频提示词，并调用大模型或 ComfyUI 的后端接口。",
    debug=settings.debug,
    docs_url="/docs",
)

setup_cors(app)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
async def ensure_storage_directory() -> None:
    """Create storage directory for temporary assets."""
    Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)
