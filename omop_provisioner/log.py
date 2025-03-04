import logging
import sys, os

from omop_provisioner.config import Config

config = Config()


# suppress "AttributeError: module 'bcrypt' has no attribute '__about__'"-warning
# https://github.com/pyca/bcrypt/issues/684
logging.getLogger("passlib").setLevel(logging.ERROR)


def get_loglevel():
    return os.getenv("LOG_LEVEL", config.LOG_LEVEL)


log = None


def get_logger(name: str = config.APP_NAME) -> logging.Logger:
    global log
    if log is None or log.name != name:
        log = logging.getLogger(name)
        log.setLevel(get_loglevel())
        log.addHandler(logging.StreamHandler(sys.stdout))
    return log
