from contextlib import asynccontextmanager
from database_asses import create_db_and_tables
from api_asses import router
from fastapi import FastAPI




@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="College Lost & Found API",
    description="FastAPI REST API for managing lost and found items",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(router)