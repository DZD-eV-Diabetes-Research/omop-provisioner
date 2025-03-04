from typing import Literal, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    APP_NAME: str = "OMOP Postgres Provisioner"
    LOG_LEVEL: Literal["INFO", "DEBUG"] = Field(default="INFO")
    POSTGRESQL_HOST: str = Field(default="localhost")
    POSTGRESQL_USER: str = Field(default="omop")
    POSTGRESQL_DATABASE: str = Field(default="omop")
    POSTGRESQL_PASSWORD: str = Field(default="omop")
    POSTGRESQL_PORT: int = Field(default=5432)
    POSTGRESQL_SCHEMA: str = Field(default="public")

    def get_sql_url(self, no_password: bool = False):
        return f"postgresql+pg8000://{self.POSTGRESQL_USER}:{'****' if no_password else self.POSTGRESQL_PASSWORD}@{self.POSTGRESQL_HOST}/{self.POSTGRESQL_DATABASE}"

    OMOP_VERSION: Optional[Literal["5.3", "5.4"]] = "5.4"
    LOAD_VOCABULARY: bool = False
    VOCABULARY_DIR: Optional[str] = None
    TRUNCATE_TABLES_ON_START: bool = False
    FORCE_SCHEMA_DEPLOYMENT: bool = False
