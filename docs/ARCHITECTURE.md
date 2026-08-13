# System Architecture

## Overview

DK Travel follows a modern three-tier architecture:

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│   Frontend   │────▶│   Backend    │────▶│  Database   │
│  (React SPA) │◀────│ (Python API) │◀────│ (MongoDB)   │
└─────────────┘     └──────────────┘     └────────────┘
```

## Frontend
- **Framework:** React 18 with Vite
- **Styling:** Tailwind CSS
- **State Management:** React Context API
- **Routing:** React Router v6
- **HTTP Client:** Axios

## Backend
- **Runtime:** Python 3.11+
- **Framework:** Flask / FastAPI
- **Authentication:** JWT-based auth
- **Validation:** Pydantic models

## Database
- **Primary Store:** MongoDB Atlas
- **ODM:** PyMongo / Motor (async)

## Deployment
- **Frontend:** Vercel (auto-deploy from main)
- **Backend:** Render (Docker container)
- **CI/CD:** GitHub Actions
