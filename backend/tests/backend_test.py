"""Wanderly Phase 0 POC — backend integration tests."""
import base64
import io
import os
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values
from PIL import Image

# ---------- Config ----------
frontend_env = dotenv_values("/app/frontend/.env")
BASE_URL = (
    os.environ.get("REACT_APP_BACKEND_URL")
    or frontend_env.get("REACT_APP_BACKEND_URL")
).rstrip("/")

TEST_PHOTOS = [Path(f"/tmp/test_photo_{i}.jpg") for i in range(1, 6)]
COLLAGE_TIMEOUT = 180  # Gemini vision may take a while

TEMPLATES = [
    "polaroid_scrapbook", "magazine", "postcard",
    "filmstrip", "moodboard", "film_photo",
]
VALID_VIBES = {"friends_trip", "couple", "solo", "family",
               "adventure", "beach", "mountains", "city"}


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    return s


def _photo_files(n=3):
    """Open n test photo files for multipart upload."""
    return [
        ("files", (p.name, open(p, "rb"), "image/jpeg"))
        for p in TEST_PHOTOS[:n]
    ]


# ---------- Basic health ----------
class TestHealth:
    def test_docs(self, api):
        r = api.get(f"{BASE_URL}/api/docs", timeout=15)
        assert r.status_code == 200
        assert "swagger" in r.text.lower() or "openapi" in r.text.lower()

    def test_health(self, api):
        r = api.get(f"{BASE_URL}/api/health", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is True
        assert data["gmail_configured"] is True
        assert data["gemini_configured"] is True
        assert set(data["templates"]) == set(TEMPLATES)


# ---------- Email invite ----------
class TestEmailInvite:
    def test_send_invite_success(self, api):
        payload = {
            "to_email": "sayanbhatt2005@gmail.com",
            "recipient_name": "Sayan",
            "trip_name": "TEST_ Wanderly POC Verification",
            "organizer_name": "QA Bot",
            "destination": "Goa, India",
            "dates": "March 12 — March 16, 2026",
        }
        r = api.post(f"{BASE_URL}/api/test/send-invite-email",
                     json=payload, timeout=60)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["success"] is True
        assert isinstance(data["message_id"], str) and len(data["message_id"]) > 5
        assert isinstance(data["sent_at"], str) and len(data["sent_at"]) > 5

    def test_invalid_email_returns_422(self, api):
        payload = {
            "to_email": "not-an-email",
            "recipient_name": "X",
            "trip_name": "T",
            "organizer_name": "O",
            "destination": "D",
            "dates": "Dates",
        }
        r = api.post(f"{BASE_URL}/api/test/send-invite-email",
                     json=payload, timeout=30)
        assert r.status_code == 422


# ---------- Collage generation ----------
class TestCollage:
    def _post_collage(self, api, n_photos=3, template="polaroid_scrapbook"):
        files = _photo_files(n_photos)
        try:
            r = api.post(
                f"{BASE_URL}/api/test/generate-collage",
                params={"template": template},
                files=files,
                timeout=COLLAGE_TIMEOUT,
            )
        finally:
            for _, fh in files:
                try:
                    fh[1].close()
                except Exception:
                    pass
        return r

    def _validate_response(self, data, template):
        assert data["template_used"] == template
        assert data["vibe"] in VALID_VIBES
        assert isinstance(data["caption"], str) and len(data["caption"]) > 0
        assert isinstance(data["quote"], str) and len(data["quote"]) > 0
        assert isinstance(data["dominant_colors"], list)
        assert len(data["dominant_colors"]) == 3
        for c in data["dominant_colors"]:
            assert isinstance(c, str) and c.startswith("#") and len(c) == 7
        assert data["collage_base64"].startswith("data:image/png;base64,")
        assert "/api/static/collages/" in data["collage_url"]
        assert data["collage_url"].endswith(".png")
        assert 0.0 <= data["confidence"] <= 1.0

    def _validate_dimensions(self, b64_data_url):
        b64 = b64_data_url.split(",", 1)[1]
        img = Image.open(io.BytesIO(base64.b64decode(b64)))
        assert img.size == (1080, 1920), f"got {img.size}"

    def test_polaroid_scrapbook_full(self, api):
        r = self._post_collage(api, 3, "polaroid_scrapbook")
        assert r.status_code == 200, r.text
        data = r.json()
        self._validate_response(data, "polaroid_scrapbook")
        self._validate_dimensions(data["collage_base64"])
        # verify URL is reachable and serves image/png
        rr = requests.get(data["collage_url"], timeout=30)
        assert rr.status_code == 200
        assert rr.headers.get("content-type", "").startswith("image/png")
        img = Image.open(io.BytesIO(rr.content))
        assert img.size == (1080, 1920)

    def test_only_2_photos_returns_400(self, api):
        r = self._post_collage(api, 2, "polaroid_scrapbook")
        assert r.status_code == 400
        assert "at least 3" in r.text.lower() or "3" in r.text

    def test_6_photos_returns_400(self, api):
        # duplicate 5 → 6 files
        files = _photo_files(5) + [
            ("files", (TEST_PHOTOS[0].name, open(TEST_PHOTOS[0], "rb"), "image/jpeg"))
        ]
        try:
            r = api.post(
                f"{BASE_URL}/api/test/generate-collage",
                params={"template": "polaroid_scrapbook"},
                files=files,
                timeout=COLLAGE_TIMEOUT,
            )
        finally:
            for _, fh in files:
                try:
                    fh[1].close()
                except Exception:
                    pass
        assert r.status_code == 400
        assert "5" in r.text or "at most" in r.text.lower()

    def test_invalid_template_returns_422(self, api):
        r = self._post_collage(api, 3, "nonsense")
        assert r.status_code == 422

    @pytest.mark.parametrize("template", [
        "magazine", "postcard", "filmstrip", "moodboard", "film_photo",
    ])
    def test_other_templates(self, api, template):
        r = self._post_collage(api, 3, template)
        assert r.status_code == 200, r.text
        data = r.json()
        self._validate_response(data, template)
        self._validate_dimensions(data["collage_base64"])
