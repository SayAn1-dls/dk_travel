"""Application-wide constants for Wanderly."""

from typing import Dict, List

# Application metadata
APP_NAME = "Wanderly"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-Powered Travel Companion"

# API configuration
API_PREFIX = "/api/v1"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Rate limiting
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW_SECONDS = 60

# Cache TTL (seconds)
CACHE_TTL_SHORT = 300      # 5 minutes
CACHE_TTL_MEDIUM = 1800    # 30 minutes
CACHE_TTL_LONG = 3600      # 1 hour
CACHE_TTL_DAY = 86400      # 24 hours

# Supported currencies
SUPPORTED_CURRENCIES: List[str] = [
    "USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD", "CHF",
    "CNY", "SEK", "NZD", "MXN", "SGD", "HKD", "NOK", "KRW",
    "TRY", "RUB", "BRL", "ZAR", "AED", "THB", "MYR", "PHP",
    "IDR", "VND", "EGP", "PKR", "BDT", "LKR",
]

# Exchange rates (base: USD)
EXCHANGE_RATES: Dict[str, float] = {
    "USD": 1.0, "EUR": 0.92, "GBP": 0.79, "INR": 83.12,
    "JPY": 149.50, "AUD": 1.53, "CAD": 1.36, "CHF": 0.88,
    "CNY": 7.24, "SEK": 10.45, "NZD": 1.63, "MXN": 17.15,
    "SGD": 1.34, "HKD": 7.82, "NOK": 10.55, "KRW": 1320.50,
    "TRY": 27.05, "RUB": 96.50, "BRL": 4.97, "ZAR": 18.90,
    "AED": 3.67, "THB": 35.20, "MYR": 4.65, "PHP": 55.80,
    "IDR": 15450.0, "VND": 24300.0, "EGP": 30.90, "PKR": 285.50,
    "BDT": 110.0, "LKR": 325.0,
}

# Hotel star ratings
HOTEL_STAR_RATINGS = [1, 2, 3, 4, 5]

# Hotel amenities
HOTEL_AMENITIES: List[str] = [
    "WiFi", "Pool", "Spa", "Gym", "Restaurant", "Bar",
    "Room Service", "Parking", "Airport Shuttle", "Pet Friendly",
    "Business Center", "Laundry", "Concierge", "Beach Access",
    "Mountain View", "City View", "Breakfast Included",
]

# Flight classes
FLIGHT_CLASSES = ["Economy", "Premium Economy", "Business", "First"]

# Popular destinations
POPULAR_DESTINATIONS: List[Dict[str, str]] = [
    {"city": "Paris", "country": "France", "code": "CDG"},
    {"city": "Tokyo", "country": "Japan", "code": "NRT"},
    {"city": "New York", "country": "USA", "code": "JFK"},
    {"city": "London", "country": "UK", "code": "LHR"},
    {"city": "Dubai", "country": "UAE", "code": "DXB"},
    {"city": "Singapore", "country": "Singapore", "code": "SIN"},
    {"city": "Bangkok", "country": "Thailand", "code": "BKK"},
    {"city": "Istanbul", "country": "Turkey", "code": "IST"},
    {"city": "Rome", "country": "Italy", "code": "FCO"},
    {"city": "Bali", "country": "Indonesia", "code": "DPS"},
    {"city": "Mumbai", "country": "India", "code": "BOM"},
    {"city": "Sydney", "country": "Australia", "code": "SYD"},
]

# Weather condition icons mapping
WEATHER_ICONS = {
    "clear": "☀️", "clouds": "☁️", "rain": "🌧️",
    "drizzle": "🌦️", "thunderstorm": "⛈️", "snow": "❄️",
    "mist": "🌫️", "fog": "🌫️", "haze": "🌫️",
}

# Blog categories
BLOG_CATEGORIES: List[str] = [
    "Adventure", "Cultural", "Food & Drink", "Budget Travel",
    "Luxury", "Solo Travel", "Family", "Backpacking",
    "Road Trip", "Beach", "Mountain", "City Guide",
    "Tips & Tricks", "Packing Guide", "Photography",
]

# Review rating labels
RATING_LABELS = {
    1: "Poor", 2: "Fair", 3: "Good", 4: "Very Good", 5: "Excellent",
}
