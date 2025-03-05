from typing import Literal, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Configuration settings for the OMOP Postgres Provisioner."""

    APP_NAME: str = Field(
        default="OMOP Postgres Provisioner", description="Name of the application."
    )
    LOG_LEVEL: Literal["INFO", "DEBUG"] = Field(
        default="INFO", description="Logging level. Can be 'INFO' or 'DEBUG'."
    )
    POSTGRESQL_HOST: str = Field(
        default="localhost",
        description="Hostname or IP address of the PostgreSQL server.",
    )
    POSTGRESQL_USER: str = Field(
        default="omop", description="Username for PostgreSQL authentication."
    )
    POSTGRESQL_DATABASE: str = Field(
        default="omop", description="Name of the PostgreSQL database."
    )
    POSTGRESQL_PASSWORD: str = Field(
        default="omop", description="Password for PostgreSQL authentication."
    )
    POSTGRESQL_PORT: int = Field(
        default=5432, description="Port number on which PostgreSQL is running."
    )
    POSTGRESQL_SCHEMA: str = Field(
        default="public", description="Schema within the PostgreSQL database to use."
    )
    OMOP_VERSION: Optional[Literal["5.3", "5.4"]] = Field(
        default="5.4",
        description="OMOP Common Data Model (CDM) version to use. Options: '5.3' or '5.4'.",
    )
    LOAD_VOCABULARY: bool = Field(
        default=False,
        description="Whether to load OMOP vocabulary during initialization.",
    )
    VOCABULARY_SOURCE: Optional[str] = Field(
        default=None,
        description="Local path, zip file, or URL containing an OMOP Athena Vocabulary export.",
    )
    TRUNCATE_TABLES_ON_START: bool = Field(
        default=False,
        description="If True, truncates OMOP tables at startup before loading new data.",
    )
    FORCE_SCHEMA_DEPLOYMENT: bool = Field(
        default=False,
        description="If True, forces re-deployment of the database schema.",
    )

    def get_sql_url(self, no_password: bool = False) -> str:
        """Generates the SQLAlchemy-compatible PostgreSQL connection URL."""
        password = "****" if no_password else self.POSTGRESQL_PASSWORD
        return f"postgresql+pg8000://{self.POSTGRESQL_USER}:{password}@{self.POSTGRESQL_HOST}/{self.POSTGRESQL_DATABASE}"
