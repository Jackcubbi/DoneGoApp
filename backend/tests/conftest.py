"""Pytest configuration and shared fixtures for the DoneGo backend."""
import os

# Set required env vars BEFORE any app module is imported so pydantic-settings
# can initialise Settings without needing the real .env file.
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# StaticPool reuses a single connection so in-memory tables survive across requests
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Create all tables once for the test session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client():
    """Return a TestClient with the DB dependency overridden."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def registered_user(client):
    """Register a test user and return their credentials."""
    payload = {
        "name": "Testi",
        "surname": "Käyttäjä",
        "email": "testi@example.com",
        "phone": "+358401234567",
        "password": "salasana123",
    }
    resp = client.post("/api/register", json=payload)
    assert resp.status_code == 201, resp.text
    return payload


@pytest.fixture(scope="session")
def auth_headers(client, registered_user):
    """Login and return Authorization headers."""
    resp = client.post(
        "/api/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
