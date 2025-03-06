from typing import Dict, List, Optional
from pathlib import Path
import os
import sys
from sqlalchemy import create_engine, inspect, schema
from omopmodel import VocabulariesLoader

if __name__ == "__main__":
    # Add this directory to global Python modules.
    # This way we address this directory becomes a temporary "installed" python module and can be referenced by its name
    # e.g. "from bbApprove import config"
    MODULE_DIR = Path(__file__).parent
    MODULE_PARENT_DIR = MODULE_DIR.parent.absolute()
    sys.path.insert(0, os.path.normpath(MODULE_PARENT_DIR))
from omop_provisioner.atlas_data_source_injector import AtlasDataSourceInjector
from omop_provisioner.db import get_ohdsi_webapi_sql_url, get_omop_sql_url, get_engine

from omop_provisioner.config import Config
from omop_provisioner.db import (
    truncate_db,
    set_table_schema_search_path,
    create_schema_if_not_exists,
)
from omop_provisioner.log import get_logger
from omop_provisioner.omop_provisioner_state import (
    OmopProvisionerState,
    get_state,
    update_state,
)
from omop_provisioner.athena_vocab_file_handler import AthenaVocabFileHandler


log = get_logger()
config = Config()
if config.OMOP_VERSION == "5.4":
    log.info("Import OMOP schema 5.4")
    from omopmodel import OMOP_5_4_declarative as omop
elif config.OMOP_VERSION == "5.3":
    log.info("Import OMOP schema 5.4")
    from omopmodel import OMOP_5_3_declarative as omop
engine = get_engine(get_omop_sql_url(), schema_name=config.POSTGRESQL_SCHEMA)

# omop.Base.metadata.schema = config.POSTGRESQL_SCHEMA
create_schema_if_not_exists(engine, config.POSTGRESQL_SCHEMA)
set_table_schema_search_path(omop, config.POSTGRESQL_SCHEMA)
omop_provisioner_state: OmopProvisionerState = get_state(engine)
log.debug(
    ("omop_provisioner_state", type(omop_provisioner_state), omop_provisioner_state)
)

if not omop_provisioner_state.schema_version_deployed or config.FORCE_SCHEMA_DEPLOYMENT:
    log.info(
        f"Deploy OMPO Schema to database '{get_omop_sql_url(censor_password=True)}'"
    )
    # Create the OMOP Schema on our database
    omop.Base.metadata.create_all(engine)
    omop_provisioner_state.schema_version_deployed = config.OMOP_VERSION
    omop_provisioner_state = update_state(engine, omop_provisioner_state)

if config.TRUNCATE_TABLES_ON_START:
    log.info("Truncate all OMOP tables because TRUNCATE_TABLES_ON_START=True")
    truncate_db(engine=engine)

if config.LOAD_VOCABULARY:
    if not omop_provisioner_state.vocabulary_loaded:
        vocab_file_handler = AthenaVocabFileHandler(config.VOCABULARY_SOURCE)
        vocab_file_path = vocab_file_handler.get_vocab_csvs_path()
        log.debug(f"vocab_file_path: {vocab_file_path}")
        if vocab_file_path:
            v = VocabulariesLoader(
                vocab_file_path,
                database_engine=engine,
                omop_module=omop,
                truncate_vocabulary_tables_before_insert=True,
            )
            log.info("Load Athena Vocabulary. This can take some time...")
            v.load_all()
            log.info("... done loading Athena Vocabulary.")
        omop_provisioner_state.vocabulary_loaded = True
        omop_provisioner_state = update_state(engine, omop_provisioner_state)


if config.LOG_LEVEL == "DEBUG":
    inspector = inspect(engine)
    log.debug("Following tables exists in database:")
    log.debug(inspector.get_table_names())

if config.OHDSI_WEBAPI_REGISTER_DATASOURCE:
    atlas_schema_name = (
        config.OHDSI_WEBAPI_POSTGRESQL_SCHEMA or config.POSTGRESQL_SCHEMA
    )
    log.info(
        f"""Register OMOP DB ('{get_ohdsi_webapi_sql_url(auth_style=None,scheme="")}', postgres-schema: '{config.POSTGRESQL_SCHEMA}') as data source in OHSDI WEBAPI DB ('{get_ohdsi_webapi_sql_url(auth_style=None,scheme="")}', postgres-schema: '{config.OHDSI_WEBAPI_POSTGRESQL_SCHEMA or config.POSTGRESQL_SCHEMA}')."""
    )
    atlas_db_url = get_ohdsi_webapi_sql_url()
    source_injector = AtlasDataSourceInjector(
        atlas_db_url=atlas_db_url, atlas_db_schema_name=atlas_schema_name
    )
    source_injector.add_source()


log.info("OMOP Provisioner done running successful. Will exit with 0...")
