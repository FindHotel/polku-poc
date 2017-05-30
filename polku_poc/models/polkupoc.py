"""Data models for Polku's PoC app."""

# pylint: disable=invalid-name,too-few-public-methods,no-member,E0611


from sqlalchemy import (
    DateTime,
    Column,
    Integer,
    String,
)

from polku_poc.settings import config
from .base import Base


SCHEMA = "polkupoc_{}".format(config.context["env"].stage.lower())


class Client(Base):

    """Client events."""

    __tablename__ = "client"
    __table_args__ = {"schema": SCHEMA}

    message_id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime)
    user_id = Column(String(36))
    user_name = Column(String(80))
    type = Column(String(80))
    event = Column(String(80))


class Server(Base):

    """Server events."""

    __tablename__ = "server"
    __table_args__ = {"schema": SCHEMA}

    message_id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime)
    user_id = Column(String(36))
    user_name = Column(String(80))
    type = Column(String(80))
    event = Column(String(80))


class Log(Base):

    """Log events."""

    __tablename__ = "log"
    __table_args__ = {"schema": SCHEMA}

    id = Column(String(128), primary_key=True)
    log_group = Column(String(1024))
    log_stream = Column(String(1024))
    received_at = Column(DateTime)
    timestamp = Column(DateTime)
    message = Column(String(1024))
