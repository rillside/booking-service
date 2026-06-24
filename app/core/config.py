from environs import Env

env = Env()
env.read_env()


class Settings:
    POSTGRES_USER: str = env.str("POSTGRES_USER")
    POSTGRES_PASSWORD: str = env.str("POSTGRES_PASSWORD")
    POSTGRES_DB: str = env.str("POSTGRES_DB")
    POSTGRES_HOST: str = env.str("POSTGRES_HOST", default="localhost")
    POSTGRES_PORT: int = env.int("POSTGRES_PORT", default=5432)

    SECRET_KEY: str = env.str("SECRET_KEY")
    ALGORITHM: str = env.str("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = env.int(
        "ACCESS_TOKEN_EXPIRE_MINUTES", default=60
    )

    ADMIN_LOGIN: str = env.str("ADMIN_LOGIN")
    ADMIN_HASHED_PASSWORD: str = env.str("ADMIN_HASHED_PASSWORD")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
