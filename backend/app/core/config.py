from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "OpenEcom-RPA"
    env: str = "dev"
    debug: bool = True

    # 数据库：默认 SQLite 便于本地起，Docker 里用 postgresql
    database_url: str = "sqlite:///./open_ecom_rpa.db"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # 开发模式：True 时 Celery 同步执行，不需要起 Redis / worker
    celery_always_eager: bool = True

    # 浏览器
    playwright_headless: bool = True

    # 平台凭据（从 .env 读，已 gitignore）
    temu_account: str = ""
    temu_password: str = ""


settings = Settings()
