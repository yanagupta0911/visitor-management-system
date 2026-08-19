from tests.conftest import STAFF_EMAIL, STAFF_PASSWORD


def test_signup_success(client):
    resp = client.post(
        "/auth/signup",
        data={"name": "Alice", "email": "alice@example.com", "password": "Str0ng!Pass1"},
    )
    assert resp.status_code == 201
    assert "user_id" in resp.json()


def test_signup_rejects_weak_password(client):
    resp = client.post(
        "/auth/signup",
        data={"name": "Alice", "email": "alice2@example.com", "password": "weak"},
    )
    assert resp.status_code == 400


def test_signup_rejects_invalid_email(client):
    resp = client.post(
        "/auth/signup",
        data={"name": "Alice", "email": "not-an-email", "password": "Str0ng!Pass1"},
    )
    assert resp.status_code == 400


def test_signup_rejects_duplicate_email(client):
    data = {"name": "Alice", "email": "dup@example.com", "password": "Str0ng!Pass1"}
    client.post("/auth/signup", data=data)
    resp = client.post("/auth/signup", data=data)
    assert resp.status_code == 400


def test_login_success(client):
    client.post(
        "/auth/signup",
        data={"name": "Bob", "email": "bob@example.com", "password": "Str0ng!Pass1"},
    )
    resp = client.post("/auth/login", data={"email": "bob@example.com", "password": "Str0ng!Pass1"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_does_not_reveal_which_field_was_wrong(client):
    client.post(
        "/auth/signup",
        data={"name": "Bob", "email": "bob2@example.com", "password": "Str0ng!Pass1"},
    )
    wrong_password = client.post(
        "/auth/login", data={"email": "bob2@example.com", "password": "WrongPass1!"}
    )
    unknown_email = client.post(
        "/auth/login", data={"email": "unknown@example.com", "password": "WrongPass1!"}
    )
    assert wrong_password.status_code == 400
    assert unknown_email.status_code == 400
    assert wrong_password.json()["detail"] == unknown_email.json()["detail"]


def test_login_locks_out_after_repeated_failures(client):
    client.post(
        "/auth/signup",
        data={"name": "Carl", "email": "carl@example.com", "password": "Str0ng!Pass1"},
    )
    for _ in range(5):
        resp = client.post("/auth/login", data={"email": "carl@example.com", "password": "WrongPass1!"})
        assert resp.status_code == 400

    locked = client.post("/auth/login", data={"email": "carl@example.com", "password": "WrongPass1!"})
    assert locked.status_code == 429

    # Even the correct password is rejected while locked out.
    still_locked = client.post("/auth/login", data={"email": "carl@example.com", "password": "Str0ng!Pass1"})
    assert still_locked.status_code == 429


def test_me_requires_auth(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client, auth_headers):
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == STAFF_EMAIL


def test_password_change_requires_correct_current_password(client, auth_headers):
    resp = client.put(
        "/auth/password",
        headers=auth_headers,
        data={"current_password": "WrongPass1!", "new_password": "NewPass1!"},
    )
    assert resp.status_code == 400


def test_password_change_and_relogin(client, auth_headers):
    resp = client.put(
        "/auth/password",
        headers=auth_headers,
        data={"current_password": STAFF_PASSWORD, "new_password": "NewPass1!"},
    )
    assert resp.status_code == 200

    relogin = client.post("/auth/login", data={"email": STAFF_EMAIL, "password": "NewPass1!"})
    assert relogin.status_code == 200
