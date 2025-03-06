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

    OHDSI_WEBAPI_REGISTER_DATASOURCE: bool = False
    OHDSI_WEBAPI_DATASOURCE_NAME: Optional[str] = Field(
        default="OMOP-importer", description="The name of the Atlas WEBAPI Datasource"
    )
    OHDSI_WEBAPI_POSTGRESQL_HOST: Optional[str] = Field(
        default=None,
        description="Hostname or IP address of the OHDSI WebAPI PostgreSQL server.",
    )
    OHDSI_WEBAPI_POSTGRESQL_USER: Optional[str] = Field(
        default=None, description="Username for OHDSI WebAPI PostgreSQL authentication."
    )
    OHDSI_WEBAPI_POSTGRESQL_DATABASE: Optional[str] = Field(
        default=None, description="Name of the OHDSI WebAPI PostgreSQL database."
    )
    OHDSI_WEBAPI_POSTGRESQL_PASSWORD: Optional[str] = Field(
        default=None, description="Password for OHDSI WebAPI PostgreSQL authentication."
    )
    OHDSI_WEBAPI_POSTGRESQL_PORT: Optional[int] = Field(
        default=None,
        description="Port number on which OHDSI WebAPI PostgreSQL is running.",
    )
    OHDSI_WEBAPI_POSTGRESQL_SCHEMA: Optional[str] = Field(
        default=None,
        description="Schema within the OHDSI WebAPI PostgreSQL database to use.",
    )

    def get_webapi_sql_url(
        self, hide_password: bool = False, scheme: str = "postgresql+pg8000://"
    ) -> str:
        """Generates the SQLAlchemy-compatible PostgreSQL connection URL."""
        password = (
            "****"
            if hide_password
            else self.OHDSI_WEBAPI_POSTGRESQL_PASSWORD or self.POSTGRESQL_PASSWORD
        )
        return f"{scheme}{self.OHDSI_WEBAPI_POSTGRESQL_HOST or self.POSTGRESQL_USER}:{password}@{self.OHDSI_WEBAPI_POSTGRESQL_HOST or self.POSTGRESQL_HOST}:{self.OHDSI_WEBAPI_POSTGRESQL_PORT or self.POSTGRESQL_HOST}/{self.OHDSI_WEBAPI_POSTGRESQL_DATABASE or self.POSTGRESQL_DATABASE}"

    def get_sql_url(
        self, hide_password: bool = False, scheme: str = "postgresql+pg8000://"
    ) -> str:
        """Generates the SQLAlchemy-compatible PostgreSQL connection URL."""
        password = "****" if hide_password else self.POSTGRESQL_PASSWORD
        return f"{scheme}{self.POSTGRESQL_USER}:{password}@{self.POSTGRESQL_HOST}:{self.POSTGRESQL_HOST}/{self.POSTGRESQL_DATABASE}"
