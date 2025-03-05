from sqlalchemy import (
    Date,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
    Boolean,
    SmallInteger,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
import decimal
from sqlalchemy import select, update, Engine
from sqlalchemy.orm import Session
from omop_provisioner.config import Config
from omop_provisioner.log import get_logger

log = get_logger()
config = Config()


if config.OMOP_VERSION == "5.4":
    from omopmodel import OMOP_5_4_declarative as omop
elif config.OMOP_VERSION == "5.3":
    from omopmodel import OMOP_5_3_declarative as omop


class OmopProvisionerState(omop.Base):
    __tablename__ = "_omop_provsioner_state"
    __table_args__ = {
        "comment": "meta table from https://github.com/DZD-eV-Diabetes-Research/omop-provisioner . Just ignore this if you dont know what this is for :) "
    }
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="PLaceholder PK. We only have one row here",
        server_default=text("1"),
    )
    schema_version_deployed: Mapped[str] = mapped_column(
        String(16),
        comment="The OMOP Schema Version that was deployed on this DB",
        server_default="",
    )
    vocabulary_loaded: Mapped[Boolean] = mapped_column(
        Boolean,
        comment="True if vocabulary was loaded.",
        server_default=text("false"),
    )


def get_state(engine: Engine) -> OmopProvisionerState:
    omop.Base.metadata.create_all(engine, tables=[OmopProvisionerState.__table__])
    query = select(OmopProvisionerState).limit(1)
    state = None
    with Session(engine, expire_on_commit=False) as session:
        state = session.get(OmopProvisionerState, 1)
        if state is None:
            log.debug("No _omop_provsioner_state. Create OmopProvisionerState entry.")
            state = OmopProvisionerState()
            session.add(state)
            session.commit()
            state = session.get(OmopProvisionerState, 1)
        log.debug(f"State before expunge: {state.__dict__}")
        session.expunge(state)

    return state


def update_state(engine: Engine, state: OmopProvisionerState) -> OmopProvisionerState:
    with Session(engine) as session:
        session.add(state)
        session.commit()
    return get_state(engine)
