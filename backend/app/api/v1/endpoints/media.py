"""素材上传与处理接口。"""

from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ....schemas.media import MediaProcessingMode, MediaUploadResponse
from ....services.comfyui import ComfyUIClient, ComfyUIError
from ....services.storage import StorageService
from ....utils.identifiers import new_job_id

router = APIRouter()

storage_service = StorageService()
comfy_client = ComfyUIClient()


@router.post(
    "/media/upload",
    response_model=MediaUploadResponse,
    summary="上传素材并生成提示",
)
async def upload_media(
    file: UploadFile = File(...),
    mode: MediaProcessingMode = Form(default=MediaProcessingMode.direct),
    comfyui_endpoint: Optional[str] = Form(default=None),
    notes: Optional[str] = Form(default=None),
) -> MediaUploadResponse:
    """保存上传的媒体文件，并在需要时触发 ComfyUI 处理。"""
    job_id, path = storage_service.persist_upload(file, job_id=new_job_id("media"))

    comfy_status = None
    if mode == MediaProcessingMode.comfy:
        try:
            comfy_status = await comfy_client.submit_workflow(
                payload={"prompt": {"file_path": str(path), "notes": notes}},
                endpoint_override=comfyui_endpoint,
            )
        except ComfyUIError as exc:
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    detail = "Stored for direct processing" if mode == MediaProcessingMode.direct else "Forwarded to ComfyUI"
    response = MediaUploadResponse(
        job_id=job_id,
        filename=path.name,
        mode=mode,
        comfyui_endpoint=comfyui_endpoint,
        detail=detail,
    )

    if comfy_status:
        response.detail = f"{detail}. ComfyUI status: {comfy_status.get('status', 'unknown')}"

    return response
