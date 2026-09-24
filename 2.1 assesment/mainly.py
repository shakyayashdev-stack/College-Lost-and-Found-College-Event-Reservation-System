from contextlib import asynccontextmanager

from fastapi import FastAPI

from database_asses import create_db_and_tables
from api_asses import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="College Event Reservation API",
    description="API for managing college events and student reservations",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(router)