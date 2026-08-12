# 🌍 Wanderly — AI-Powered Travel Companion

[![CI](https://github.com/SayAn1-dls/dk_travel/actions/workflows/ci.yml/badge.svg)](https://github.com/SayAn1-dls/dk_travel/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)

> Plan smarter. Travel better. Share memories beautifully.

Wanderly is a full-stack travel platform that helps users discover destinations, plan itineraries, search flights and hotels, and create stunning photo collages of their journeys — all powered by AI.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     WANDERLY PLATFORM                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   React SPA  │  │ React Native │  │   Admin UI   │  │
│  │  (frontend/) │  │  (mobile/)   │  │  (planned)   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │          │
│         └────────┬────────┴────────┬────────┘          │
│                  │    REST API     │                    │
│         ┌────────▼─────────────────▼────────┐          │
│         │        FastAPI Backend             │          │
│         │  ┌─────────┐  ┌────────────────┐  │          │
│         │  │ Routes   │  │  Services      │  │          │
│         │  │ hotels   │  │  collage_svc   │  │          │
│         │  │ flights  │  │  email_svc     │  │          │
│         │  │ itinerary│  │  vibe_svc      │  │          │
│         │  │ reviews  │  │  weather_svc   │  │          │
│         │  │ blog     │  │  currency_svc  │  │          │
│         │  └─────────┘  └────────────────┘  │          │
│         └────────┬──────────────────────────┘          │
│                  │                                      │
│         ┌────────▼────────┐  ┌──────────────┐          │
│         │    MongoDB      │  │  Gemini AI   │          │
│         │  (Motor async)  │  │  (vibe/photo)│          │
│         └─────────────────┘  └──────────────┘          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Status | Description |
|---------|--------|-------------|
| 🏨 Hotel Search | ✅ | Search and filter hotels by destination, price, rating |
| ✈️ Flight Search | ✅ | Compare flights with flexible date search |
| 📋 Itinerary Planner | ✅ | Drag-and-drop trip planning with day-by-day organization |
| ⭐ Reviews & Ratings | ✅ | Community reviews for destinations and hotels |
| 🌤️ Weather Forecasts | ✅ | 5-day weather forecasts for any destination |
| 💱 Currency Converter | ✅ | Real-time currency conversion for 30+ currencies |
| 📝 Travel Blog | ✅ | Read and write travel stories and guides |
| 🎨 Photo Collages | ✅ | AI-powered travel photo collage generator |
| 📧 Email Invites | ✅ | Beautiful Pinterest-style trip invitation emails |
| 🤖 Vibe Analysis | ✅ | AI-powered photo mood and vibe detection |
| 📱 Mobile App | 🚧 | React Native companion app |

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** >= 18.x
- **Python** >= 3.11
- **MongoDB** (local or Atlas)
- **Git**

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your credentials
uvicorn server:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

The app will be available at `http://localhost:3000`.

---

## 📁 Project Structure

```
dk_travel/
├── frontend/           # React SPA (CRA + Craco)
│   ├── src/
│   │   ├── components/ # Reusable UI components
│   │   ├── pages/      # Route pages
│   │   ├── hooks/      # Custom React hooks
│   │   ├── context/    # React Context providers
│   │   ├── utils/      # Helper functions
│   │   └── styles/     # Global styles & themes
│   └── public/         # Static assets
├── backend/            # FastAPI Python backend
│   ├── routes/         # API route handlers
│   ├── models/         # Pydantic & MongoDB models
│   ├── middleware/     # Custom middleware
│   ├── utils/          # Backend utilities
│   ├── config/         # Configuration
│   ├── tests/          # Pytest test suite
│   └── scripts/        # Utility scripts
├── mobile/             # React Native app (Expo)
├── docs/               # API documentation
├── .github/            # GitHub Actions & templates
└── docker-compose.yml  # Container orchestration
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Tailwind CSS, Radix UI, React Router |
| Backend | FastAPI, Pydantic, Motor (async MongoDB) |
| Database | MongoDB (via Motor) |
| AI/ML | Google Gemini (vibe analysis, photo processing) |
| Email | Resend API, Gmail SMTP |
| Mobile | React Native (Expo) |
| DevOps | Docker, GitHub Actions |
| Testing | Pytest (backend), Jest (frontend) |

---

## 🧪 Running Tests

```bash
# Backend tests
cd backend
pytest --tb=short -v

# Frontend tests
cd frontend
npm test
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 👏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) — Modern Python web framework
- [React](https://reactjs.org/) — UI component library
- [Tailwind CSS](https://tailwindcss.com/) — Utility-first CSS
- [Radix UI](https://www.radix-ui.com/) — Accessible component primitives
- [Google Gemini](https://ai.google.dev/) — AI capabilities

---

<p align="center">Made with ❤️ by the Wanderly Team</p>
