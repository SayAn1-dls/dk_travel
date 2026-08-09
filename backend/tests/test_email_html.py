"""Tests for the redesigned traveler-voice invite email HTML template.

Imports `_render_html` from /app/backend/email_service.py directly and asserts
content contract (strings, fonts, size, randomization patterns, tape signer).
"""
import re

import pytest

# email_service is on sys.path via conftest.py
from email_service import _render_html


SAMPLE_ARGS = dict(
    recipient_name="Sayan",
    trip_name="Ladakh Bike Odyssey",
    organizer_name="The Wanderly Crew",
    destination="Ladakh, India",
    dates="April 5 — April 12, 2026",
    accept_url="https://wanderly.app/invite/accept?token=DEMO_TOKEN_ABC12345",
    hero_image="https://images.unsplash.com/photo-1.jpg",
    quote="I haven't been everywhere, but it's on my list.",
)


@pytest.fixture(scope="module")
def html():
    return _render_html(**SAMPLE_ARGS)


class TestInviteEmailHTML:
    # Required strings from the redesigned template
    def test_required_content_strings(self, html):
        required = [
            "PACK YOUR",
            "BOARDING PASS",
            "PASSENGER",
            "DESTINATION",
            "LUGGAGE TAG",
            "JOIN THE TRIP",
            "POSTCARD",
        ]
        for token in required:
            assert token in html, f"Missing required content string: {token!r}"
        # Footer uses &nbsp; entities between tokens — check semantically
        assert "WANDERLY" in html and "WHERE EVERY TRIP BECOMES A STORY" in html, \
            "Footer stamp text missing"
        # Verify the specific footer construction (allowing &nbsp; separators)
        assert re.search(
            r"WANDERLY(?:&nbsp;|\s)+(?://|&#47;&#47;)?\s*(?:&nbsp;|\s|/)+WHERE EVERY TRIP BECOMES A STORY",
            html,
        ), "Footer 'WANDERLY // WHERE EVERY TRIP BECOMES A STORY' not present"

    def test_font_declarations_present(self, html):
        for font in ["Fraunces", "Caveat", "Bebas Neue", "Inter"]:
            assert font in html, f"Missing font declaration: {font!r}"

    def test_google_fonts_link_present(self, html):
        assert "fonts.googleapis.com/css2?family=Fraunces" in html

    def test_html_size_under_100kb(self, html):
        size = len(html.encode("utf-8"))
        assert size < 100 * 1024, f"HTML too large: {size} bytes"

    def test_no_forbidden_fonts(self, html):
        # Case-insensitive to catch any variant
        assert "comic sans" not in html.lower(), "Forbidden font 'Comic Sans' found"

    def test_tape_signer_strips_leading_the(self, html):
        # organizer_name='The Wanderly Crew' -> signer should be 'Wanderly'
        assert "can't wait!! &mdash; Wanderly" in html, \
            "Expected tape signer to be 'Wanderly' when organizer is 'The Wanderly Crew'"
        assert "can't wait!! &mdash; The" not in html, \
            "Tape signer must not use the filler word 'The'"

    def test_uppercase_passenger_and_destination(self, html):
        assert "SAYAN" in html, "Passenger name must be uppercase in HTML"
        assert "LADAKH, INDIA" in html, "Destination must be uppercase in HTML"

    def test_randomized_flight_gate_seat(self, html):
        # Flight number 'WA-XXX' (exactly 3 digits)
        flight_match = re.search(r"FLIGHT\s+WA-(\d{3})\b", html)
        assert flight_match, "Missing flight number pattern WA-XXX"

        # Gate = one of A-F followed by digits
        gate_match = re.search(r"GATE\s+([A-F]\d+)\b", html)
        assert gate_match, "Missing gate pattern (letter A-F + digits)"

        # Seat = 1-42 followed by A-F
        seat_match = re.search(r"SEAT\s+(\d{1,2})([A-F])\b", html)
        assert seat_match, "Missing seat pattern (1-42 + A-F)"
        seat_num = int(seat_match.group(1))
        assert 1 <= seat_num <= 42, f"Seat number out of range: {seat_num}"

    def test_tape_signer_fallback_when_only_filler(self):
        # If organizer_name is only filler words, signer should fall back
        html = _render_html(**{**SAMPLE_ARGS, "organizer_name": "The"})
        assert "the crew" in html, "Fallback signer 'the crew' expected"

    def test_hero_and_accept_url_rendered(self, html):
        assert SAMPLE_ARGS["hero_image"] in html
        assert SAMPLE_ARGS["accept_url"] in html

    def test_quote_rendered(self, html):
        assert SAMPLE_ARGS["quote"] in html
