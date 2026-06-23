from environs import Env

env = Env()
env.read_env()


class Settings:
    # 1. Настройки PostgreSQL
    POSTGRES_USER: str = env.str("POSTGRES_USER")
    POSTGRES_PASSWORD: str = env.str("POSTGRES_PASSWORD")
    POSTGRES_DB: str = env.str("POSTGRES_DB")
    POSTGRES_HOST: str = env.str("POSTGRES_HOST", default="localhost")
    POSTGRES_PORT: int = env.int("POSTGRES_PORT", default=5432)

    # Динамическая сборка строки подключения к БД
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # 2. Настройки безопасности (JWT) для ТЗ ШИФТа
    # Если SECRET_KEY не задан в .env, сгенерируется дефолтный безопасный ключ
    SECRET_KEY: str = env.str(
        "SECRET_KEY", default="super-temporary-secret-key"
        )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = env.int(
        "ACCESS_TOKEN_EXPIRE_MINUTES", default=60
        )


settings = Settings()
