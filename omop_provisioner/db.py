from typing import Literal
from sqlalchemy import create_engine, inspect, event, Engine
from pg8000 import Connection
from omop_provisioner.config import Config

from sqlalchemy import Engine, schema
from omop_provisioner.omop_provisioner_state import OmopProvisionerState
from omopmodel import OMOP_5_4_declarative

config = Config()


def get_engine(url: str, schema_name: str = None) -> Engine:
    print("url", url)
    engine = create_engine(url=url)

    # Set the search_path after connection is established
    if schema_name:

        def set_search_path(dbapi_connection: Connection, connection_record):
            # Use the cursor to execute SQL to set search_path
            cursor = dbapi_connection.cursor()
            cursor.execute(f"SET search_path TO {config.POSTGRESQL_SCHEMA}")
            cursor.close()

        event.listen(engine, "connect", set_search_path)
    return engine


def create_schema_if_not_exists(engine: Engine, schema_name: str):
    con = engine.connect()
    trans = con.begin()
    if not engine.dialect.has_schema(con, schema_name):
        con.execute(schema.CreateSchema(schema_name))
    trans.commit()
    con.close()


def set_table_schema_search_path(omop: OMOP_5_4_declarative, schema_name: str):
    """Dynamically sets the schema for all tables inheriting from Base"""
    meta = omop.Base.metadata
    for table in meta.sorted_tables:
        table.schema = schema_name


def truncate_db(engine: Engine, omop: OMOP_5_4_declarative):
    # delete all table data (but keep tables)
    # we do cleanup before test 'cause if previous test errored,
    # DB can contain dust
    meta = omop.Base.metadata
    con = engine.connect()
    trans = con.begin()
    for table in meta.sorted_tables:
        if table.name == OmopProvisionerState.__tablename__:
            continue
        con.execute(f'ALTER TABLE "{table.name}" DISABLE TRIGGER ALL;')
        con.execute(table.delete())
        con.execute(f'ALTER TABLE "{table.name}" ENABLE TRIGGER ALL;')
    trans.commit()
    con.close()


def get_ohdsi_webapi_sql_url(
    censor_password: bool = False,
    scheme: str = "postgresql+pg8000://",
    auth_style: Literal["userinfo", "parameter"] | None = "userinfo",
) -> str:
    """Generates the SQLAlchemy-compatible PostgreSQL connection URL."""
    password = (
        "****"
        if censor_password
        else config.OHDSI_WEBAPI_POSTGRESQL_PASSWORD or config.POSTGRESQL_PASSWORD
    )
    username = config.OHDSI_WEBAPI_POSTGRESQL_USER or config.POSTGRESQL_USER
    userinfo = ""
    parameters = ""
    if auth_style == "userinfo":
        userinfo = f"{username}:{password}@"
    elif auth_style == "parameter":
        parameters == f"?user={username}&password={password}"

    return f"{scheme}{userinfo}{config.OHDSI_WEBAPI_POSTGRESQL_HOST or config.POSTGRESQL_HOST}:{config.OHDSI_WEBAPI_POSTGRESQL_PORT or config.POSTGRESQL_PORT}/{config.OHDSI_WEBAPI_POSTGRESQL_DATABASE or config.POSTGRESQL_DATABASE}{parameters}"


def get_omop_sql_url(
    censor_password: bool = False,
    scheme: str = "postgresql+pg8000://",
    auth_style: Literal["userinfo", "parameter"] | None = "userinfo",
) -> str:
    """Generates the SQLAlchemy-compatible PostgreSQL connection URL."""
    password = "****" if censor_password else config.POSTGRESQL_PASSWORD
    username = config.POSTGRESQL_USER
    userinfo = ""
    parameters = ""
    if auth_style == "userinfo":
        userinfo = f"{username}:{password}@"
    elif auth_style == "parameter":
        parameters == f"?user={username}&password={password}"
    return f"{scheme}{userinfo}{config.POSTGRESQL_HOST}:{config.POSTGRESQL_PORT}/{config.POSTGRESQL_DATABASE}"
