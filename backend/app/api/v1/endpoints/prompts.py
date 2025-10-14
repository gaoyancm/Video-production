"""提示词生成接口。"""

from fastapi import APIRouter, HTTPException, status

from ....schemas.prompt import PromptResponse, SubmissionTarget, TextPromptRequest
from ....services.comfyui import ComfyUIClient, ComfyUIError
from ....services.llm import LLMProvider, ProviderError

router = APIRouter()

llm_provider = LLMProvider()
comfy_client = ComfyUIClient()


@router.post("/prompts/text", response_model=PromptResponse, summary="文本生成提示词")
async def generate_prompt_from_text(payload: TextPromptRequest) -> PromptResponse:
    """根据文字输入生成结构化视频提示词。"""
    try:
        prompt_response = await llm_provider.generate_prompt(payload)
    except ProviderError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    if payload.submit_to in (SubmissionTarget.comfyui, SubmissionTarget.both):
        try:
            comfy_response = await comfy_client.submit_workflow(
                payload=build_workflow_payload(prompt_response.prompt),
                endpoint_override=payload.comfyui_endpoint,
            )
            prompt_response.metadata["comfyui_submission"] = comfy_response
        except ComfyUIError as exc:
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    if payload.submit_to in (SubmissionTarget.llm, SubmissionTarget.both):
        prompt_response.metadata.setdefault("llm_submission", {"status": "submitted"})

    return prompt_response


def build_workflow_payload(prompt: str) -> dict:
    """构造简易的 ComfyUI 工作流负载。"""
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="生成的提示词为空，无法继续处理。"
        )

    return {
        "prompt": {
            "nodes": [
                {
                    "type": "text_prompt",
                    "id": "text_prompt_1",
                    "inputs": {"text": prompt},
                }
            ]
        }
    }
