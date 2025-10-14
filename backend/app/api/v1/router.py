"""API router assembly."""

from fastapi import APIRouter

from .endpoints import health, media, prompts

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(prompts.router, tags=["prompts"])
api_router.include_router(media.router, tags=["media"])
