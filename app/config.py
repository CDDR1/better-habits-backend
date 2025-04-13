from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_username: str
    db_password: str
    db_dev_host: str
    db_prd_host: str
    db_port: int
    db_name: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()