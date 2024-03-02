import os
import pytest
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session
from google.cloud.sql.connector import Connector
from api.database import init_connection_pool, SessionLocal

def test_init_connection_pool():
    # Setup
    connector = Connector()

    # Exercise
    engine = init_connection_pool(connector)

    # Verify
    assert isinstance(engine, Engine)

def test_SessionLocal():
    # Setup
    session = SessionLocal()

    # Here we're just starting a transaction to test the session
    session.begin()

    # Verify
    # If the session is working, it should now have an active transaction
    assert session.is_active

    # Teardown
    session.close()