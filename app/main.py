from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.router import router
from app.database.database import Database
from app.api.error_handler import ErrorHandler
from app.config.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    Database.init_db()
    yield


app = FastAPI(lifespan=lifespan)

ErrorHandler.register_error_handlers(app)
app.include_router(router)
