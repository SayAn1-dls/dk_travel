"""Gemini 2.0 Flash vision — analyze uploaded photos to detect vibe + suggest caption/quote."""

from __future__ import annotations

import base64
import json
import logging
import os
import random
import re
import uuid
from typing import List

from quotes import TRAVEL_QUOTES

log = logging.getLogger(__name__)

VALID_VIBES = {
    "friends_trip", "couple", "solo", "family",
    "adventure", "beach", "mountains", "city",
}

_PROMPT = """You are Wanderly's Vibe Lab — a Pinterest-aesthetic travel curator.
You are given a set of photos from one trip. Analyze them TOGETHER as a single mood/vibe.

Return STRICT JSON with these exact keys and nothing else (no markdown fences, no prose):
{
  "vibe": "one of: friends_trip | couple | solo | family | adventure | beach | mountains | city",
  "dominant_colors": ["#RRGGBB", "#RRGGBB", "#RRGGBB"],
  "caption": "a short, poetic caption for a travel collage (max 10 words, evocative, no hashtags)",
  "quote": "a short travel quote (max 15 words) that fits the mood",
  "confidence": 0.0
}

Rules:
- Pick the single most fitting vibe from the enumerated list.
- dominant_colors must be 3 hex codes drawn from the actual photos.
- caption should read like a Pinterest photo caption (e.g. "Golden hours, salted skin").
- quote should complement the vibe (short, iconic-feeling).
- confidence in 0..1.
Output JSON ONLY.
"""


def _extract_json(text: str) -> dict:
    """Best-effort extraction of a JSON object from an LLM reply."""
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
    return json.loads(text)


def _fallback_vibe(reason: str) -> dict:
    log.warning("Vibe analysis fallback used (%s) — returning defaults", reason)
    return {
        "vibe": "friends_trip",
        "dominant_colors": ["#C65D3A", "#E8D5B7", "#2C2416"],
        "caption": "Somewhere between here and forever.",
        "quote": random.choice(TRAVEL_QUOTES),
        "confidence": 0.0,
    }


async def analyze_photos(images_b64: List[str]) -> dict:
    """
    Ask Gemini Vision to jointly analyze the photos and return {vibe, dominant_colors, caption, quote, confidence}.
    Falls back to sensible defaults if the model call or JSON parse fails.
    """
    key = os.environ.get("EMERGENT_LLM_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        return _fallback_vibe("EMERGENT_LLM_KEY / GOOGLE_API_KEY not set")

    try:
        import google.generativeai as genai
    except ImportError:
        return _fallback_vibe("google-generativeai not installed")

    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    # Build multimodal content parts
    parts = []
    for img_b64 in images_b64:
        # Strip data URI prefix if present
        if "," in img_b64 and img_b64.startswith("data:"):
            img_b64 = img_b64.split(",", 1)[1]
        try:
            img_bytes = base64.b64decode(img_b64)
        except Exception:
            continue
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_bytes).decode(),
            }
        })
    parts.append("Analyze these trip photos together and return the JSON described in the system message.")

    try:
        response = model.generate_content(
            [{"role": "user", "parts": parts}],
            generation_config={"temperature": 0.4},
        )
        reply = response.text
    except Exception as e:
        log.exception("Gemini vision call failed: %s", e)
        return _fallback_vibe(f"gemini call error: {e}")

    try:
        data = _extract_json(reply)
    except Exception as e:
        log.warning("Failed to parse Gemini JSON reply. raw=%r err=%s", reply[:400], e)
        return _fallback_vibe("json parse error")

    # Validate / sanitize
    vibe = str(data.get("vibe", "")).strip().lower()
    if vibe not in VALID_VIBES:
        vibe = "friends_trip"

    colors = data.get("dominant_colors") or []
    clean_colors: List[str] = []
    for c in colors:
        c = str(c).strip()
        if re.fullmatch(r"#[0-9a-fA-F]{6}", c):
            clean_colors.append(c.upper())
    if len(clean_colors) < 3:
        for fill in ["#C65D3A", "#E8D5B7", "#2C2416"]:
            if fill not in clean_colors:
                clean_colors.append(fill)
            if len(clean_colors) == 3:
                break
    clean_colors = clean_colors[:3]

    caption = str(data.get("caption") or "Somewhere between here and forever.").strip().strip('"').strip("'")
    if len(caption) > 120:
        caption = caption[:117] + "..."

    quote = str(data.get("quote") or random.choice(TRAVEL_QUOTES)).strip().strip('"').strip("'")
    if len(quote) > 160:
        quote = quote[:157] + "..."

    try:
        confidence = float(data.get("confidence", 0.5))
    except (TypeError, ValueError):
        confidence = 0.5
    confidence = max(0.0, min(1.0, confidence))

    return {
        "vibe": vibe,
        "dominant_colors": clean_colors,
        "caption": caption,
        "quote": quote,
        "confidence": confidence,
    }
