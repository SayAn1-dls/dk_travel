# Wanderly PRD — Phase 0 POC

## Original problem statement
Wanderly is a Pinterest-aesthetic travel super-app (web-only, fully responsive React + FastAPI + Mongo, i.e. FARM stack). Full scope spans ~7 phases: destinations, trip planning, bookings, expense split, AI Vibe Lab collages, WhatsApp-style chat, Gmail invites.

Phase 0 goal: de-risk two critical integrations BEFORE building the UI:
1. Gmail SMTP invite emails with Pinterest-aesthetic HTML
2. Gemini Vision + collage generation via Pillow

If either fails visually, we redesign before Phase 1.

## Architecture (Phase 0)
- Backend: FastAPI at `/app/backend`, all routes prefixed `/api`
  - `POST /api/test/send-invite-email` → aiosmtplib → Gmail SMTP (STARTTLS)
  - `POST /api/test/generate-collage` → emergentintegrations Gemini vision → Pillow collage
  - `GET /api/health` → configuration sanity check
  - `GET /api/docs` → Swagger UI
- Frontend: React (CRA) at `/app/frontend`
  - `/` → placeholder
  - `/poc-test` → minimal test page for both flows
- MongoDB: not used in Phase 0 (connection wired but no models yet)
- Static: `/app/backend/static/collages/*.png` served at `/api/static/collages/`

## Integrations
- **Gmail SMTP** — `smtp.gmail.com:587`, STARTTLS, app password auth (creds in `.env`)
- **Gemini vision** — via `emergentintegrations.llm.chat.LlmChat` model `gemini-2.5-flash` (closest to requested `gemini-2.0-flash` from available list) with EMERGENT_LLM_KEY

## Collage templates (6)
1. `polaroid_scrapbook` — tilted polaroids on paper, washi tape, handwritten
2. `magazine` — editorial serif layout with hero + side photos + pull quote
3. `postcard` — single photo, cream border, "Wish you were here" stamp, handwritten caption
4. `filmstrip` — vertical film-negative strip with sprocket holes (dynamic frame size)
5. `moodboard` — Pinterest-style irregular grid with rounded corners
6. `film_photo` — vintage single hero, film grain, date stamp corner, dark bg

## Fonts (bundled at /app/backend/fonts/)
- Playfair Display (Regular + Bold)
- DM Serif Display (Regular)
- Caveat (handwritten)
- Inter (Regular + Bold — Liberation Sans metric-compatible fallback used since Google Fonts CDN URL was unreliable)

## Palette
- Terracotta #C65D3A · Sand #E8D5B7 · Sage #A8B89A · Cream #FAF3E7 · Ink #2C2416

## What's implemented (Feb 2026)
- [x] Gmail SMTP endpoint with bulletproof HTML email + rotating quote + hero image
- [x] Gemini vision analysis (vibe / dominant colors / caption / quote) with structured JSON
- [x] 6 Pillow collage templates, 1080x1920, saved to disk + returned as base64 + URL
- [x] Static file serving under /api/static/collages/
- [x] `/poc-test` minimal frontend for visual verification
- [x] Input validation: 400 for <3 or >5 photos, template validation via Literal
- [x] Clear SMTP error logging
- [x] `/api/health` diagnostics endpoint

## What's NOT built (deferred to later phases)
- Landing page, auth, destinations catalog, trip planning, bookings
- Expense split, chat, real invite links / RSVP flow
- MongoDB models & persistence

## Backlog / next steps
- Phase 1: landing + auth + destinations catalog
- Phase 2: trip planning + itinerary
- Phase 3: bookings integration
- Phase 4: expense split
- Phase 5: Vibe Lab UI (using this POC's compositor)
- Phase 6: chat
- Phase 7: real invite/RSVP + Gmail integration for actual invites
