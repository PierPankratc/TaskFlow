import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db.create_db import get_db_connect
from db.models import Base

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


app.dependency_overrides[get_db_connect] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def login(client, name="testuser", password="testpass123"):
    response = client.post("/login", json={"name": name, "password": password})
    assert response.status_code == 200
    return response


@pytest.fixture
def auth_client(client):
    login(client)
    return client


@pytest.fixture
def project_id(auth_client):
    response = auth_client.post(
        "/project/add",
        json={"title": "Тестовый проект", "status": "new", "priority": "low"},
    )
    assert response.status_code == 200
    return response.json()["id"]


@pytest.fixture
def task_id(auth_client, project_id):
    response = auth_client.post(
        "/tasks/add",
        json={
            "title": "Тестовая задача",
            "project_id": project_id,
            "status": "new",
            "priority": "low",
            "deadline": None,
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


@pytest.fixture
def subtask_id(auth_client, task_id):
    response = auth_client.post(
        "/subtasks/add",
        json={
            "title": "Тестовая подзадача",
            "task_id": task_id,
            "status": "new",
            "priority": "low",
            "deadline": None,
        },
    )
    assert response.status_code == 200
    return response.json()["id"]
