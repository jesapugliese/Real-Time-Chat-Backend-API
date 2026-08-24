from fastapi import APIRouter

from app.api.routes.channels_router import router as channels_router

router = APIRouter()

router.include_router(channels_router)
