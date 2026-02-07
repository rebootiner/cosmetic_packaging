import os


class Settings:
    app_name: str = os.getenv("APP_NAME", "cosmetic-packaging-ai")
    env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@db:5432/cosmetic_packaging",
    )
    upload_dir: str = os.getenv("UPLOAD_DIR", "/tmp/cosmetic-packaging-ai/uploads")


settings = Settings()
