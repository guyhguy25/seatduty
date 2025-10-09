import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Ensure the application uses the SQLite test database during tests
TEST_DATABASE_URL = "sqlite:///./test.db"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.core.database import Base, get_db
from app.users.models import User
from app.core.security import get_password_hash
from server import app

# Create test database engine
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# Backward-compatible alias used in some tests
@pytest.fixture(scope="function")
def db(db_session):
    yield db_session

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client."""
    return TestClient(app)

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        name="Test User",
        phone="1234567890"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """Remove the SQLite test DB file after test session completes."""
    yield
    try:
        if os.path.exists("test.db"):
            os.remove("test.db")
    except Exception:
        pass
