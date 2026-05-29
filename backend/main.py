from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.core.config import settings
from app.core.security import hash_password
from app.models.user import USERS_DB


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed demo passwords on startup
    USERS_DB["admin@idp.local"]["hashed_password"] = hash_password("Admin@123")
    USERS_DB["reviewer@idp.local"]["hashed_password"] = hash_password("Review@123")
    yield


app = FastAPI(
    title="Document Intelligence Platform API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok", "service": "IDP API"}
