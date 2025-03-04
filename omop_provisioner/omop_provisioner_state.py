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
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
import decimal
from sqlalchemy import select, update, Engine
from sqlalchemy.orm import Session


class ProvisonerBase(DeclarativeBase):
    pass


class OmopProvisionerState(ProvisonerBase):
    __tablename__ = "_omop_provsioner_state"
    __table_args__ = {
        "comment": "meta table from https://github.com/DZD-eV-Diabetes-Research/omop-provisioner . Just ignore this if you dont know what this is for :) "
    }
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="PLaceholder PK. We only have one row here",
        default=1,
    )
    schema_version_deployed: Mapped[str] = mapped_column(
        String(16),
        comment="The OMOP Schema Version that was deployed on this DB",
        default="",
    )
    vocabulary_loaded: Mapped[str] = mapped_column(
        Boolean, comment="True if vocabulary was loaded.", default=False
    )


def get_state(engine: Engine) -> OmopProvisionerState:
    ProvisonerBase.metadata.create_all(engine, tables=[OmopProvisionerState])
    query = select(OmopProvisionerState).limit(1)
    state = None
    with Session(engine) as session:
        state = session.execute(query).one_or_none()
        if state is None:
            state = OmopProvisionerState()
            session.add(state)
            session.commit()
    return state


def update_state(engine: Engine, state: OmopProvisionerState):
    with Session(engine) as session:
        session.add(state)
        session.commit()
