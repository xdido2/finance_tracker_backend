from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_SCHEMA: str
    POSTGRES_POOL_SIZE: int
    POSTGRES_MAX_OVERFLOW: int
    POSTGRES_POOL_RECYCLE: int

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_S3_BUCKET: str

    AWS_DB_ENDPOINT: str
    AWS_DB: str
    AWS_DB_USER: str
    AWS_DB_PASSWORD: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: float

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.AWS_DB_USER}:{self.AWS_DB_PASSWORD}"
            f"@{self.AWS_DB_ENDPOINT}:{self.POSTGRES_PORT}/{self.AWS_DB}"
        )
        # return (
        #     f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
        #     f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        # )

    @property
    def DATABASE_SYNC_URL(self) -> str:
        # return (
        #     f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
        #     f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        # )
        return (
            f"postgresql+psycopg2://{self.AWS_DB_USER}:{self.AWS_DB_PASSWORD}"
            f"@{self.AWS_DB_ENDPOINT}:{self.POSTGRES_PORT}/{self.AWS_DB}"
        )

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
    )


settings = Settings()
