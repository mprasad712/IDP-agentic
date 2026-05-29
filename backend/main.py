from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.core.config import settings


async def _ensure_database_exists():
    """Create the 'idp' database if it doesn't exist yet."""
    url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "")
    userinfo, hostinfo = url.split("@")
    db_user, db_pass = userinfo.split(":", 1)
    host_port, db_name = hostinfo.rsplit("/", 1)
    host, port = (host_port.split(":") + ["5432"])[:2]

    try:
        conn = await asyncpg.connect(
            host=host, port=int(port),
            user=db_user, password=db_pass,
            database="postgres",
        )
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )
        if not exists:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"[IDP] Database '{db_name}' created.")
        await conn.close()
    except Exception as e:
        print(f"[IDP] Warning: could not auto-create database: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _ensure_database_exists()
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
