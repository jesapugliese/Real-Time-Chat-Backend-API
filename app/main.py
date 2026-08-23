from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.router import router
from app.database.database import Database
from app.api.error_handler import ErrorHandler


@asynccontextmanager
async def lifespan(app: FastAPI):
    Database.init_db()
    yield


app = FastAPI(lifespan=lifespan)

ErrorHandler.register_error_handlers(app)
app.include_router(router)
