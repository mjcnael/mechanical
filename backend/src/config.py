from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class StartupConfig(BaseModel):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True


class PostgreSQLConfig(BaseModel):
    NAME: str = "postgres"
    HOST: str = "postgresql"
    PORT: str = "5432"
    USERNAME: str = "postgres"
    PASSWORD: str = "postgres"


class JWTConfig(BaseModel):
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env.template", ".env"],
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    startup: StartupConfig = StartupConfig()
    postgresql: PostgreSQLConfig = PostgreSQLConfig()
    jwt: JWTConfig = JWTConfig()


config = Config()
