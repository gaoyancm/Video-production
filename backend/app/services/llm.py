"""LLM provider integrations for prompt生成."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx
from fastapi import status

from ..core.config import AppSettings, get_settings
from ..schemas.prompt import PromptResponse, TextPromptRequest


class ProviderError(Exception):
    """Raised when an upstream模型调用失败."""

    def __init__(self, message: str, *, status_code: int = status.HTTP_502_BAD_GATEWAY) -> None:
        super().__init__(message)
        self.status_code = status_code


def build_prompt_messages(request: TextPromptRequest) -> list[dict[str, str]]:
    """构造通用的 system/user 消息体."""
    system_content = (
        "你是一名专业的视频导演，请根据用户提供的素材描述生成完整的视频提示词。"
        "输出应包含场景氛围、镜头设计、剧情结构以及建议时长。"
    )
    user_content = request.text.strip()
    if request.reference_style:
        user_content += f"\n参考风格：{request.reference_style}"
    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]


@dataclass
class ProviderResponse:
    prompt: str
    metadata: Dict[str, Any]


class BaseLLMClient:
    """公共逻辑."""

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    async def generate_prompt(self, request: TextPromptRequest) -> ProviderResponse:  # pragma: no cover - interface
        raise NotImplementedError


class OpenAIClient(BaseLLMClient):
    """调用 OpenAI Chat Completions 接口."""

    async def generate_prompt(self, request: TextPromptRequest) -> ProviderResponse:
        if not self.settings.openai_api_key:
            raise ProviderError("未配置 OpenAI API Key。")

        model_name = request.target_model or self.settings.default_openai_model
        payload = {
            "model": model_name,
            "messages": build_prompt_messages(request),
            "temperature": 0.6,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(base_url=self.settings.openai_base_url, timeout=60) as client:
            response = await client.post("/chat/completions", headers=headers, json=payload)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:  # pragma: no cover - network
                raise ProviderError(f"OpenAI 调用失败：{exc.response.text}") from exc

        data = response.json()
        prompt_text = data["choices"][0]["message"]["content"].strip()

        metadata = {
            "provider": "openai",
            "model": model_name,
            "usage": data.get("usage", {}),
        }
        return ProviderResponse(prompt=prompt_text, metadata=metadata)


class DashScopeClient(BaseLLMClient):
    """调用通义千问 DashScope 兼容接口."""

    async def generate_prompt(self, request: TextPromptRequest) -> ProviderResponse:
        if not self.settings.dashscope_api_key:
            raise ProviderError("未配置 DashScope API Key。")

        model_name = request.target_model or self.settings.default_dashscope_model
        payload = {
            "model": model_name,
            "messages": build_prompt_messages(request),
            "temperature": 0.6,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.dashscope_api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(base_url=self.settings.dashscope_base_url, timeout=60) as client:
            response = await client.post("/chat/completions", headers=headers, json=payload)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:  # pragma: no cover - network
                raise ProviderError(f"DashScope 调用失败：{exc.response.text}") from exc

        data = response.json()
        prompt_text = data["choices"][0]["message"]["content"].strip()
        metadata = {
            "provider": "dashscope",
            "model": model_name,
            "request_id": data.get("id"),
        }
        return ProviderResponse(prompt=prompt_text, metadata=metadata)


class GeminiClient(BaseLLMClient):
    """调用 Google Gemini 生成式 API."""

    async def generate_prompt(self, request: TextPromptRequest) -> ProviderResponse:
        if not self.settings.gemini_api_key:
            raise ProviderError("未配置 Gemini API Key。")

        model_name = request.target_model or self.settings.default_gemini_model

        system_prompt, user_prompt = build_prompt_messages(request)
        payload = {
            "contents": [
                {"role": system_prompt["role"], "parts": [{"text": system_prompt["content"]}]},
                {"role": user_prompt["role"], "parts": [{"text": user_prompt["content"]}]},
            ],
            "generationConfig": {
                "temperature": 0.6,
                "topK": 40,
                "topP": 0.9,
            },
        }

        endpoint = (
            f"{self.settings.gemini_api_base_url}/models/{model_name}:generateContent"
            f"?key={self.settings.gemini_api_key}"
        )

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(endpoint, json=payload)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:  # pragma: no cover - network
                raise ProviderError(f"Gemini 调用失败：{exc.response.text}") from exc

        data = response.json()
        try:
            prompt_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError) as exc:  # pragma: no cover - defensive
            raise ProviderError(f"Gemini 返回数据缺失：{json.dumps(data, ensure_ascii=False)}") from exc

        metadata = {
            "provider": "gemini",
            "model": model_name,
            "safety_ratings": data["candidates"][0].get("safetyRatings", []),
        }
        return ProviderResponse(prompt=prompt_text, metadata=metadata)


class LLMProvider:
    """多模型路由器."""

    def __init__(self, settings: Optional[AppSettings] = None) -> None:
        self.settings = settings or get_settings()
        self.clients: Dict[str, BaseLLMClient] = {
            "openai": OpenAIClient(self.settings),
            "dashscope": DashScopeClient(self.settings),
            "tongyi": DashScopeClient(self.settings),
            "gemini": GeminiClient(self.settings),
        }

    async def generate_prompt(self, request: TextPromptRequest) -> PromptResponse:
        provider_key = self._pick_provider(request)
        client = self.clients.get(provider_key)
        if not client:
            raise ProviderError(f"暂不支持的模型提供商：{provider_key}", status_code=status.HTTP_400_BAD_REQUEST)

        provider_response = await client.generate_prompt(request)
        metadata = provider_response.metadata
        if request.reference_style:
            metadata["reference_style"] = request.reference_style
        if request.target_model:
            metadata["requested_model"] = request.target_model

        return PromptResponse(prompt=provider_response.prompt, metadata=metadata)

    def _pick_provider(self, request: TextPromptRequest) -> str:
        """结合 target_model 和配置选择提供商 key."""
        if request.target_model:
            lowered = request.target_model.lower()
            if lowered in self.clients:
                return lowered
            # 针对 openai/兼容模型名称做推断
            if lowered.startswith("gpt"):
                return "openai"
            if lowered.startswith("qwen"):
                return "dashscope"
            if lowered.startswith("gemini"):
                return "gemini"

        # 按可用配置优先级选取
        if self.settings.openai_api_key:
            return "openai"
        if self.settings.dashscope_api_key:
            return "dashscope"
        if self.settings.gemini_api_key:
            return "gemini"
        return "openai"
