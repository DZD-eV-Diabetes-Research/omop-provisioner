from sqlalchemy import text, TextClause, Connection
from omop_provisioner.config import Config
from omop_provisioner.utils import string_to_slug
from omop_provisioner.db import get_engine, get_ohdsi_webapi_sql_url, get_omop_sql_url

config = Config()


class AtlasDataSourceInjector:
    def __init__(self, atlas_db_url: str, atlas_db_schema_name: str):
        self.atlas_db_url = atlas_db_url
        self.atlas_db_schema_name = atlas_db_schema_name

    def add_source(self):
        atlas_db_engine = get_engine(self.atlas_db_url, self.atlas_db_schema_name)
        con = atlas_db_engine.connect()
        trans = con.begin()
        if atlas_db_engine.dialect.has_schema(con, self.atlas_db_schema_name):
            if self._source_allready_registered(con):
                con.close()
                return
            con.execute(self._gen_sql_statement())
        trans.commit()
        con.close()

    def _gen_source_identifier(self) -> str:
        return string_to_slug(config.OHDSI_WEBAPI_DATASOURCE_NAME)

    def _source_allready_registered(self, connection: Connection):
        query = f"SELECT source_key FROM {self.atlas_db_schema_name}.source WHERE source_key = '{self._gen_source_identifier()}'"
        result = connection.execute(text(query))
        rows = result.fetchall()
        if len(rows) == 0:
            return False
        return True

    def _gen_sql_statement(self) -> TextClause:

        return text(
            f"""
        INSERT INTO {self.atlas_db_schema_name}.source (source_id, source_name, source_key, source_connection, source_dialect, username, password) 
        SELECT nextval('{self.atlas_db_schema_name}.source_sequence'), '{config.OHDSI_WEBAPI_DATASOURCE_NAME}', '{self._gen_source_identifier()}', ' {get_omop_sql_url(scheme='jdbc:postgresql://',auth_style=None)}', 'postgresql','{config.POSTGRESQL_USER}','{config.POSTGRESQL_PASSWORD}';

        INSERT INTO {self.atlas_db_schema_name}.source_daimon (source_daimon_id, source_id, daimon_type, table_qualifier, priority) 
        SELECT nextval('{self.atlas_db_schema_name}.source_daimon_sequence'), source_id, 0, 'cdm', 0
        FROM {self.atlas_db_schema_name}.source
        WHERE source_key = '{self._gen_source_identifier()}'
        ;

        INSERT INTO {self.atlas_db_schema_name}.source_daimon (source_daimon_id, source_id, daimon_type, table_qualifier, priority) 
        SELECT nextval('{self.atlas_db_schema_name}.source_daimon_sequence'), source_id, 1, 'vocab', 1
        FROM {self.atlas_db_schema_name}.source
        WHERE source_key = '{self._gen_source_identifier()}'
        ;

        INSERT INTO {self.atlas_db_schema_name}.source_daimon (source_daimon_id, source_id, daimon_type, table_qualifier, priority) 
        SELECT nextval('{self.atlas_db_schema_name}.source_daimon_sequence'), source_id, 2, 'results', 1
        FROM {self.atlas_db_schema_name}.source
        WHERE source_key = '{self._gen_source_identifier()}'
        ;
        """
        )
