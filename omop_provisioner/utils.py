import importlib
from sqlalchemy import MetaData, Engine
from omop_provisioner.omop_provisioner_state import OmopProvisionerState


def import_module_by_path_name(import_: str, from_: str = None):
    if from_:
        module = importlib.import_module(from_)
        return getattr(module, import_)
    else:
        return importlib.import_module(import_)


def truncate_db(engine: Engine):
    # delete all table data (but keep tables)
    # we do cleanup before test 'cause if previous test errored,
    # DB can contain dust
    meta = MetaData(bind=engine, reflect=True)
    con = engine.connect()
    trans = con.begin()
    for table in meta.sorted_tables:
        if table.name == OmopProvisionerState.__tablename__:
            continue
        con.execute(f'ALTER TABLE "{table.name}" DISABLE TRIGGER ALL;')
        con.execute(table.delete())
        con.execute(f'ALTER TABLE "{table.name}" ENABLE TRIGGER ALL;')
    trans.commit()
