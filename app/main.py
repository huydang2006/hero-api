from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app import models  # noqa: F401
from app.database import engine
from app.routers import heroes, missions, teams


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Hero API",
    version="1.0.0",
    description="A REST API for heroes, teams, and missions.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(heroes.router, prefix="/api/v1")
app.include_router(missions.router, prefix="/api/v1")
app.include_router(teams.router, prefix="/api/v1")
