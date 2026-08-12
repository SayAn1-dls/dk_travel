# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-08-12

### Added
- Hotel search API with filtering (destination, price, rating, amenities)
- Flight search API with flexible date queries
- Itinerary planner with full CRUD operations
- Reviews and ratings system for destinations and hotels
- Weather forecast integration (5-day forecasts)
- Currency converter supporting 30+ currencies
- Travel blog with CRUD operations
- Frontend pages: Hotels, Flights, Itinerary, Blog
- Reusable components: SearchBar, FilterPanel, HotelCard, FlightCard
- WeatherWidget and CurrencyConverter widgets
- Custom hooks: useSearch, useItinerary
- TravelContext for global state management
- API client utility with base URL configuration
- Rate limiting middleware
- In-memory cache middleware
- Input validation and response formatting utilities
- Structured logging system
- Docker and docker-compose setup
- GitHub Actions CI/CD pipelines
- Comprehensive API documentation
- Database seed script with sample data
- ESLint and Prettier configuration
- Light/dark theme support

## [0.2.0] - 2026-08-10

### Added
- Email invitation service with Pinterest-aesthetic HTML templates
- Photo collage generator (AI-powered via Gemini)
- Vibe analysis service for travel photos
- React Native mobile app scaffold (Expo)
- MongoDB integration with Motor async driver

## [0.1.0] - 2026-08-08

### Added
- Initial project setup
- FastAPI backend with basic structure
- React frontend with Tailwind CSS and Radix UI
- Basic routing and navigation
- POC test page for email and collage features
