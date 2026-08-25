from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.router import router
from app.database.database import Database
from app.api.error_handler import ErrorHandler
from app.config.logging import configure_logging
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    Database.init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

ErrorHandler.register_error_handlers(app)
app.include_router(router)
