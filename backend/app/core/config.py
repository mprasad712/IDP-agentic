from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "idp-super-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    FRONTEND_URL: str = "http://localhost:5173"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password123@localhost:5432/idp"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
