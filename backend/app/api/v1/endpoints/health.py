"""健康检查接口。"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="服务健康检查")
async def healthcheck() -> dict[str, str]:
    """返回服务状态，用于存活探针。"""
    return {"status": "ok"}
