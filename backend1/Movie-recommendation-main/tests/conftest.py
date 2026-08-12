import pytest
import os
from fastapi.testclient import TestClient

from app.database.connection import engine, SessionLocal, get_db
from app.database.base import Base
from app.main import app
from app.utils.seed import seed_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    # Ensure standard DB is initialized and seeded for test suite
    seed_db()
    yield

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
