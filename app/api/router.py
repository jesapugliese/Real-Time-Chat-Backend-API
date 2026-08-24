from fastapi import APIRouter

from app.api.routes.channels_router import router as channels_router
from app.api.routes.messages_router import router as messages_router


router = APIRouter()

router.include_router(channels_router)
router.include_router(messages_router)
