from typing import Literal
import importlib
from sqlalchemy import MetaData, Engine, schema
from omop_provisioner.omop_provisioner_state import OmopProvisionerState
import os
import tempfile
import requests
import zipfile
import re
from omopmodel import OMOP_5_4_declarative


def import_module_by_path_name(import_: str, from_: str = None):
    if from_:
        module = importlib.import_module(from_)
        return getattr(module, import_)
    else:
        return importlib.import_module(import_)


def string_to_slug(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
