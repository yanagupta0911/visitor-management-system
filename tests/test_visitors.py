import io
import os

from tests.conftest import FAKE_JPEG_BYTES, FAKE_PNG_BYTES, VALID_VISITOR_FORM


def create_visitor(client, auth_headers, **overrides):
    data = {**VALID_VISITOR_FORM, **overrides}
    resp = client.post("/visitors", headers=auth_headers, data=data)
    assert resp.status_code == 201, resp.text
    return resp.json()["visitor_id"]


def test_create_requires_auth(client):
    resp = client.post("/visitors", data=VALID_VISITOR_FORM)
    assert resp.status_code == 401


def test_create_rejects_invalid_phone(client, auth_headers):
    resp = client.post(
        "/visitors", headers=auth_headers, data={**VALID_VISITOR_FORM, "phone": "12345"}
    )
    assert resp.status_code == 400


def test_create_rejects_invalid_email(client, auth_headers):
    resp = client.post(
        "/visitors", headers=auth_headers, data={**VALID_VISITOR_FORM, "email": "nope"}
    )
    assert resp.status_code == 400


def test_create_success_records_registration_metadata(client, auth_headers):
    visitor_id = create_visitor(client, auth_headers)
    resp = client.get(f"/visitors/{visitor_id}", headers=auth_headers)
    body = resp.json()
    assert body["status"] == "Registered"
    assert body["registered_date"]
    assert body["registered_time"]
    assert body["registered_by"] == "Test Staff"


def test_list_requires_auth(client):
    resp = client.get("/visitors")
    assert resp.status_code == 401


def test_get_single_visitor_not_found(client, auth_headers):
    resp = client.get("/visitors/VIS-DOESNOTEXIST", headers=auth_headers)
    assert resp.status_code == 404


def test_update_visitor(client, auth_headers):
    visitor_id = create_visitor(client, auth_headers)
    resp = client.put(
        f"/visitors/{visitor_id}",
        headers=auth_headers,
        data={**VALID_VISITOR_FORM, "name": "Jane Updated"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Jane Updated"


def test_update_rejects_invalid_phone(client, auth_headers):
    visitor_id = create_visitor(client, auth_headers)
    resp = client.put(
        f"/visitors/{visitor_id}",
        headers=auth_headers,
        data={**VALID_VISITOR_FORM, "phone": "bad"},
    )
    assert resp.status_code == 400


def test_checkin_requires_auth(client, auth_headers):
    visitor_id = create_visitor(client, auth_headers)
    resp = client.post(
        f"/visitors/{visitor_id}/checkin",
        files={"photo": ("photo.jpg", io.BytesIO(FAKE_JPEG_BYTES), "image/jpeg")},
    )
    assert resp.status_code == 401


def test_checkin_rejects_disallowed_extension(client, auth_headers):
    visitor_id = create_visitor(client, auth_headers)
    resp = client.post(
        f"/visitors/{visitor_id}/checkin",
        headers=auth_headers,
        files={"photo": ("payload.txt", io.BytesIO(b"not an image"), "text/plain")},
    )
    assert resp.status_code == 400


def test_checkin_rejects_content_that_does_not_match_extension(client, auth_headers):
    visitor_id = create_visitor(client, auth_headers)
    # ".jpg" extension but the bytes are plain text, not a real JPEG header.
    resp = client.post(
        f"/visitors/{visitor_id}/checkin",
        headers=auth_headers,
        files={"photo": ("fake.jpg", io.BytesIO(b"this is not a jpeg"), "image/jpeg")},
    )
    assert resp.status_code == 400


def test_checkin_rejects_oversized_photo(client, auth_headers, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "MAX_PHOTO_SIZE_MB", 0)  # anything is "too big"
    visitor_id = create_visitor(client, auth_headers)
    resp = client.post(
        f"/visitors/{visitor_id}/checkin",
        headers=auth_headers,
        files={"photo": ("photo.jpg", io.BytesIO(FAKE_JPEG_BYTES), "image/jpeg")},
    )
    assert resp.status_code == 400


def test_checkin_then_checkout_flow(client, auth_headers):
    visitor_id = create_visitor(client, auth_headers)

    checkin_resp = client.post(
        f"/visitors/{visitor_id}/checkin",
        headers=auth_headers,
        files={"photo": ("photo.jpg", io.BytesIO(FAKE_JPEG_BYTES), "image/jpeg")},
    )
    assert checkin_resp.status_code == 200
    body = checkin_resp.json()
    assert body["status"] == "Checked In"
    assert body["checkin_by"] == "Test Staff"

    checkout_resp = client.put(
        f"/visitors/{visitor_id}/checkout",
        headers=auth_headers,
        files={"photo": ("photo.png", io.BytesIO(FAKE_PNG_BYTES), "image/png")},
    )
    assert checkout_resp.status_code == 200
    out_body = checkout_resp.json()
    assert out_body["status"] == "Checked Out"
    assert out_body["checkout_by"] == "Test Staff"


def test_photo_upload_ignores_client_supplied_path_traversal_filename(client, auth_headers, tmp_path):
    from app.config import settings

    visitor_id = create_visitor(client, auth_headers)
    resp = client.post(
        f"/visitors/{visitor_id}/checkin",
        headers=auth_headers,
        files={"photo": ("../../evil.jpg", io.BytesIO(FAKE_JPEG_BYTES), "image/jpeg")},
    )
    assert resp.status_code == 200
    stored_path = resp.json()["checkin_photo"]
    # The stored path must stay inside the configured photo directory.
    assert os.path.commonpath(
        [os.path.abspath(stored_path), os.path.abspath(settings.CHECKIN_PHOTO_DIR)]
    ) == os.path.abspath(settings.CHECKIN_PHOTO_DIR)


def test_photo_endpoint_requires_auth(client, auth_headers):
    visitor_id = create_visitor(client, auth_headers)
    client.post(
        f"/visitors/{visitor_id}/checkin",
        headers=auth_headers,
        files={"photo": ("photo.jpg", io.BytesIO(FAKE_JPEG_BYTES), "image/jpeg")},
    )
    resp = client.get(f"/visitors/{visitor_id}/photo/checkin")
    assert resp.status_code == 401


def test_photo_endpoint_returns_image(client, auth_headers):
    visitor_id = create_visitor(client, auth_headers)
    client.post(
        f"/visitors/{visitor_id}/checkin",
        headers=auth_headers,
        files={"photo": ("photo.jpg", io.BytesIO(FAKE_JPEG_BYTES), "image/jpeg")},
    )
    resp = client.get(f"/visitors/{visitor_id}/photo/checkin", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/jpeg"


def test_public_lookup_requires_matching_email(client, auth_headers):
    visitor_id = create_visitor(client, auth_headers)

    good = client.get(f"/visitors/lookup?visitor_id={visitor_id}&email={VALID_VISITOR_FORM['email']}")
    assert good.status_code == 200

    bad = client.get(f"/visitors/lookup?visitor_id={visitor_id}&email=someone-else@example.com")
    assert bad.status_code == 404


def test_public_lookup_does_not_require_auth(client, auth_headers):
    visitor_id = create_visitor(client, auth_headers)
    resp = client.get(f"/visitors/lookup?visitor_id={visitor_id}&email={VALID_VISITOR_FORM['email']}")
    assert resp.status_code == 200


def test_delete_visitor(client, auth_headers):
    visitor_id = create_visitor(client, auth_headers)
    resp = client.delete(f"/visitors/{visitor_id}", headers=auth_headers)
    assert resp.status_code == 200

    gone = client.get(f"/visitors/{visitor_id}", headers=auth_headers)
    assert gone.status_code == 404
