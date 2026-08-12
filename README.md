# DK Travel 🌍✈️

A full-stack travel planning and booking platform built with FastAPI and React.

## Features

- **Destination Discovery**: Browse and search 1000+ travel destinations across India
- **Smart Booking**: Seamless booking with multiple payment methods (UPI, Cards, Net Banking)
- **Trip Itineraries**: AI-powered itinerary planning with budget tracking
- **Reviews & Ratings**: Community-driven reviews with photo uploads
- **Weather Integration**: Real-time weather data and best travel window recommendations
- **Interactive Maps**: Visual destination exploration with distance calculations
- **Notifications**: Multi-channel alerts (Email, SMS, Push) for bookings and reminders
- **User Profiles**: Personalized travel preferences, badges, and travel levels

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **ORM**: SQLAlchemy + Alembic migrations
- **Auth**: JWT with bcrypt password hashing
- **Testing**: pytest + pytest-asyncio

### Frontend
- **Framework**: React 18
- **State Management**: Context API + useReducer
- **Routing**: React Router v6
- **HTTP Client**: Axios with interceptors
- **Styling**: CSS Modules

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Reverse Proxy**: Nginx

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/SayAn1-dls/dk_travel.git
cd dk_travel

# Start all services
docker compose up -d

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

## Project Structure

```
dk_travel/
├── backend/
│   ├── app/
│   │   ├── core/          # Config, exceptions, logging
│   │   ├── models/        # Database & data models
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Business logic
│   │   ├── middleware/    # Cache, rate limiting, auth
│   │   └── db/            # Database & migrations
│   ├── tests/             # Unit & integration tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── context/       # State management
│   │   ├── services/      # API client
│   │   └── utils/         # Helpers & formatters
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .github/workflows/     # CI/CD pipelines
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/auth/register` | POST | User registration |
| `/api/v1/auth/login` | POST | User login |
| `/api/v1/destinations` | GET | List destinations |
| `/api/v1/destinations/:id` | GET | Destination details |
| `/api/v1/bookings` | POST | Create booking |
| `/api/v1/bookings/:id` | GET | Booking details |
| `/api/v1/reviews` | POST | Submit review |
| `/api/v1/itineraries` | POST | Create itinerary |

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Author

**Sayan Bhatt** - [GitHub](https://github.com/SayAn1-dls)
