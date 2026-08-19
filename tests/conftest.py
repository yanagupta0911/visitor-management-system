import os

# Must be set before importing the app so JWT signing works regardless of
# whether a real .env has been configured in this environment.
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base, get_db
from app.main import app

# Importing app.main above already ran Base.metadata.create_all() and the
# startup migration against the *real* app.database.engine (pointed at the
# project's actual visitor.db). Both are idempotent no-ops on an
# already-migrated database, so this is safe — but every test below runs
# against its own isolated in-memory database via the override below, and
# never touches that real file or the real photo folders.


@pytest.fixture()
def client(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    monkeypatch.setattr(settings, "CHECKIN_PHOTO_DIR", str(tmp_path / "checkin_photos"))
    monkeypatch.setattr(settings, "CHECKOUT_PHOTO_DIR", str(tmp_path / "checkout_photos"))

    from app.routers.auth import _login_attempts

    _login_attempts.clear()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


STAFF_EMAIL = "staff@example.com"
STAFF_PASSWORD = "Str0ng!Pass1"


@pytest.fixture()
def auth_headers(client):
    client.post(
        "/auth/signup",
        data={"name": "Test Staff", "email": STAFF_EMAIL, "password": STAFF_PASSWORD},
    )
    resp = client.post("/auth/login", data={"email": STAFF_EMAIL, "password": STAFF_PASSWORD})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


VALID_VISITOR_FORM = {
    "name": "Jane Roe",
    "email": "jane@example.com",
    "phone": "9876543210",
    "address": "42 Main St",
    "authority": "Reception",
    "id_name": "Passport",
    "id_no": "Z7654321",
}

# Doesn't need to be a fully-decodable JPEG — save_photo only checks that
# the file starts with the JPEG magic bytes, so this is enough to exercise
# the "valid upload" path in tests.
FAKE_JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 64
FAKE_PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
