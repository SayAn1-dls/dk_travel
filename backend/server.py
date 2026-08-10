"""Wanderly — Phase 0 POC backend.

Two proof-of-concept endpoints under `/api`:
  - POST /api/test/send-invite-email    → Gmail SMTP + Pinterest-aesthetic HTML invite
  - POST /api/test/generate-collage     → Gemini vision + Pillow 1080x1920 collage
"""

from __future__ import annotations

import base64
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Literal

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from starlette.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# Local modules
from collage_service import (  # noqa: E402
    VALID_TEMPLATES,
    compose_collage,
    image_to_data_url,
    save_collage,
)
from email_service import send_invite_email  # noqa: E402
from vibe_service import analyze_photos  # noqa: E402

# ---------- logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
log = logging.getLogger("wanderly")

# ---------- Mongo (optional — test endpoints work without it) ----------
mongo_url = os.environ.get("MONGO_URL", "")
if mongo_url:
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get("DB_NAME", "wanderly")]
else:
    log.warning("MONGO_URL not set — database features disabled")
    client = None
    db = None

# ---------- static dir ----------
STATIC_DIR = ROOT_DIR / "static"
COLLAGE_DIR = STATIC_DIR / "collages"
COLLAGE_DIR.mkdir(parents=True, exist_ok=True)


def static_url(*path_parts: str) -> str:
    """Return a host-relative URL under `/api/static/...`.

    Always return a relative path — never absolute — so the URL works on any host
    (public preview, internal cluster hostname, localhost). Clients (browser or
    otherwise) can resolve it against whatever base they used to reach the API.
    """
    clean = "/".join(p.strip("/") for p in path_parts if p)
    return f"/api/static/{clean}"

# ---------- app ----------
app = FastAPI(
    title="Wanderly API — Phase 0 POC",
    description="Proof-of-concept endpoints for Gmail SMTP invites and Vibe Lab collages.",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
)

api_router = APIRouter(prefix="/api")

# Mount static (collages) under /api/static so nginx ingress routes to backend
app.mount("/api/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ==================================================================================
# Models
# ==================================================================================

class InviteEmailRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    to_email: EmailStr
    recipient_name: str = Field(..., min_length=1, max_length=80)
    trip_name: str = Field(..., min_length=1, max_length=120)
    organizer_name: str = Field(..., min_length=1, max_length=80)
    destination: str = Field(..., min_length=1, max_length=120)
    dates: str = Field(..., min_length=1, max_length=80)


class InviteEmailResponse(BaseModel):
    success: bool
    message_id: str
    sent_at: str


class CollageResponse(BaseModel):
    vibe: str
    caption: str
    quote: str
    dominant_colors: List[str]
    template_used: str
    collage_base64: str
    collage_url: str
    collage_id: str
    confidence: float


TemplateName = Literal[
    "polaroid_scrapbook", "magazine", "postcard", "filmstrip", "moodboard", "film_photo",
]

# ==================================================================================
# Routes
# ==================================================================================

@api_router.get("/")
async def root():
    return {
        "app": "Wanderly API",
        "phase": "0 — POC",
        "status": "ok",
        "endpoints": ["/api/test/send-invite-email", "/api/test/generate-collage"],
    }


@api_router.get("/health")
async def health():
    resend_set = bool(os.environ.get("RESEND_API_KEY"))
    llm_set = bool(os.environ.get("EMERGENT_LLM_KEY"))
    return {
        "ok": True,
        "resend_configured": resend_set,
        "gemini_configured": llm_set,
        "templates": sorted(VALID_TEMPLATES),
    }


@api_router.post("/test/send-invite-email", response_model=InviteEmailResponse)
async def send_invite_email_route(body: InviteEmailRequest):
    try:
        result = await send_invite_email(
            to_email=body.to_email,
            recipient_name=body.recipient_name,
            trip_name=body.trip_name,
            organizer_name=body.organizer_name,
            destination=body.destination,
            dates=body.dates,
        )
    except Exception as e:  # SMTP auth / TLS / network
        log.exception("send_invite_email failed: %s", e)
        raise HTTPException(status_code=502, detail=f"Failed to send email: {e}")

    return InviteEmailResponse(
        success=True,
        message_id=result["message_id"],
        sent_at=datetime.now(timezone.utc).isoformat(),
    )


@api_router.post("/test/generate-collage", response_model=CollageResponse)
async def generate_collage_route(
    files: List[UploadFile] = File(..., description="3 to 5 photos"),
    template: TemplateName = Query("polaroid_scrapbook"),
):
    if len(files) < 3:
        raise HTTPException(status_code=400, detail="Please upload at least 3 images.")
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Please upload at most 5 images.")

    raw_images: List[bytes] = []
    b64_for_llm: List[str] = []
    for f in files:
        data = await f.read()
        if not data:
            raise HTTPException(status_code=400, detail=f"Empty file: {f.filename}")
        raw_images.append(data)
        b64_for_llm.append(base64.b64encode(data).decode("ascii"))

    log.info("Collage: analyzing %d images with Gemini vision (template=%s)", len(raw_images), template)
    vibe_info = await analyze_photos(b64_for_llm)
    log.info("Collage: vibe=%s caption=%r quote=%r",
             vibe_info["vibe"], vibe_info["caption"], vibe_info["quote"])

    try:
        collage_img = compose_collage(
            raw_images,
            template=template,
            caption=vibe_info["caption"],
            quote=vibe_info["quote"],
        )
    except Exception as e:
        log.exception("Collage composition failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Collage composition failed: {e}")

    collage_id, saved_path = save_collage(collage_img, COLLAGE_DIR)
    data_url = image_to_data_url(collage_img)

    # Return a HOST-RELATIVE URL so it works on public, internal, and localhost
    # (see static_url() docstring for rationale).
    collage_url = static_url("collages", f"{collage_id}.png")

    return CollageResponse(
        vibe=vibe_info["vibe"],
        caption=vibe_info["caption"],
        quote=vibe_info["quote"],
        dominant_colors=vibe_info["dominant_colors"],
        template_used=template,
        collage_base64=data_url,
        collage_url=collage_url,
        collage_id=collage_id,
        confidence=vibe_info["confidence"],
    )


# ---------- register + middleware ----------
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()
