"""ComfyUI server client."""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx
from fastapi import status

from ..core.config import AppSettings, get_settings


class ComfyUIError(Exception):
    """Raised when ComfyUI 调用失败."""

    def __init__(self, message: str, status_code: int = status.HTTP_502_BAD_GATEWAY) -> None:
        super().__init__(message)
        self.status_code = status_code


class ComfyUIClient:
    """与 ComfyUI 服务器交互的简单封装."""

    def __init__(self, settings: Optional[AppSettings] = None) -> None:
        self.settings = settings or get_settings()

    async def submit_workflow(
        self,
        payload: Dict[str, Any],
        endpoint_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """提交工作流到 ComfyUI。

        ComfyUI 服务器地址会经常变化，因此优先使用 endpoint_override。
        如果未提供 override，则尝试使用配置中的 comfyui_base_url。
        """
        base_url = (endpoint_override or "").strip() or (self.settings.comfyui_base_url or "").strip()
        if not base_url:
            raise ComfyUIError("未提供 ComfyUI 服务器地址，请在请求中填写。", status.HTTP_400_BAD_REQUEST)

        async with httpx.AsyncClient(base_url=base_url, timeout=120) as client:
            response = await client.post("/prompt", json=payload)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:  # pragma: no cover - network
                raise ComfyUIError(f"ComfyUI 调用失败：{exc.response.text}") from exc
        return response.json()
