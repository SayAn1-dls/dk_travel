"""Shared fixtures for backend tests. Generates sample photo files before tests run."""
import sys
from pathlib import Path

from PIL import Image

# Make backend modules (email_service, quotes, etc.) importable.
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def pytest_configure(config):
    """Generate 5 sample JPEG photos in /tmp for collage tests."""
    colors = [
        (200, 100, 90),
        (90, 140, 180),
        (180, 170, 100),
        (100, 180, 130),
        (170, 110, 180),
    ]
    for i, color in enumerate(colors, start=1):
        path = Path(f"/tmp/test_photo_{i}.jpg")
        if not path.exists():
            img = Image.new("RGB", (800, 800), color)
            img.save(path, "JPEG", quality=85)
