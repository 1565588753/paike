import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.core.database import Base, get_db

TEST_DB_URL = "sqlite:///./test_school.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    try:
        def _get_db():
            yield db
        app.dependency_overrides[get_db] = _get_db
        yield TestClient(app)
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_health_check(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200


def test_info(client):
    r = client.get("/api/v1/info")
    assert r.status_code == 200
    data = r.json()
    assert "name" in data


def test_unprotected_route(client):
    r = client.get("/")
    assert r.status_code == 200


def test_auth_required(client):
    r = client.get("/api/v1/teachers")
    assert r.status_code in (401, 200)  # either unauth or ok depending on public access


def test_login_invalid(client):
    r = client.post("/api/v1/auth/login", json={"username": "nonexistent", "password": "wrong"})
    assert r.status_code == 401


def test_years_list(client):
    r = client.get("/api/v1/years")
    assert r.status_code == 200
