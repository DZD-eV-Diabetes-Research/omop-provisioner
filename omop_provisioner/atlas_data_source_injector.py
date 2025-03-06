from omop_provisioner.config import Config
from omop_provisioner.utils import slug

config = Config()


class AtlasDataSourceInjector:
    def __init__(self, atlas_db_url: str, atlas_db_schema: str):
        self.atlas_db_url = atlas_db_url
        self.atlas_db_schema = atlas_db_schema

    def add_source(self):
        f"""
        INSERT INTO webapi.source (source_id, source_name, source_key, source_connection, source_dialect) 
SELECT nextval('webapi.source_sequence'), '{config.OHDSI_WEBAPI_DATASOURCE_NAME}', 'MY_CDM', ' {config.get_sql_url(scheme='jdbc:postgresql://')}', 'postgresql';

INSERT INTO webapi.source_daimon (source_daimon_id, source_id, daimon_type, table_qualifier, priority) 
SELECT nextval('webapi.source_daimon_sequence'), source_id, 0, 'cdm', 0
FROM webapi.source
WHERE source_key = 'MY_CDM'
;

INSERT INTO webapi.source_daimon (source_daimon_id, source_id, daimon_type, table_qualifier, priority) 
SELECT nextval('webapi.source_daimon_sequence'), source_id, 1, 'vocab', 1
FROM webapi.source
WHERE source_key = 'MY_CDM'
;

INSERT INTO webapi.source_daimon (source_daimon_id, source_id, daimon_type, table_qualifier, priority) 
SELECT nextval('webapi.source_daimon_sequence'), source_id, 2, 'results', 1
FROM webapi.source
WHERE source_key = 'MY_CDM'
;
        """
