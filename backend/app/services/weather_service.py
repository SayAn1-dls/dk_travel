"""Weather service for destination trip planning."""
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class WeatherCondition(Enum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    STORMY = "stormy"
    SNOWY = "snowy"
    FOGGY = "foggy"
    PARTLY_CLOUDY = "partly_cloudy"
    CLEAR = "clear"


@dataclass
class WeatherForecast:
    date: datetime
    condition: WeatherCondition
    temp_high_c: float
    temp_low_c: float
    humidity: float
    wind_speed_kmh: float
    precipitation_mm: float
    uv_index: int
    sunrise: str
    sunset: str


class WeatherService:
    """Provides weather data for travel planning."""

    def __init__(self, api_client, cache=None):
        self.api = api_client
        self.cache = cache

    async def get_current(
        self, latitude: float, longitude: float
    ) -> Dict:
        """Get current weather for coordinates."""
        cache_key = f"weather:current:{latitude:.2f},{longitude:.2f}"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

        data = await self.api.fetch_current(latitude, longitude)
        result = self._parse_current(data)

        if self.cache:
            await self.cache.set(cache_key, result, ttl=1800)

        return result

    async def get_forecast(
        self, latitude: float, longitude: float, days: int = 7
    ) -> List[WeatherForecast]:
        """Get multi-day forecast."""
        data = await self.api.fetch_forecast(latitude, longitude, days)
        return [self._parse_forecast_day(day) for day in data.get("days", [])]

    async def get_best_travel_window(
        self, destination_id: str, month_range: tuple = (1, 12)
    ) -> Dict:
        """Recommend the best months to visit a destination."""
        historical = await self.api.fetch_historical_averages(destination_id)

        scores = {}
        for month in range(month_range[0], month_range[1] + 1):
            month_data = historical.get(str(month), {})
            scores[month] = self._calculate_travel_score(month_data)

        best_months = sorted(scores, key=scores.get, reverse=True)[:3]

        return {
            "best_months": best_months,
            "scores": scores,
            "recommendation": self._format_recommendation(best_months),
        }

    async def check_alerts(
        self, latitude: float, longitude: float
    ) -> List[Dict]:
        """Check for weather alerts and warnings."""
        alerts = await self.api.fetch_alerts(latitude, longitude)
        return [
            {
                "severity": alert.get("severity", "unknown"),
                "event": alert.get("event", ""),
                "description": alert.get("description", ""),
                "expires": alert.get("expires", ""),
            }
            for alert in alerts
        ]

    def _parse_current(self, data: Dict) -> Dict:
        return {
            "temperature_c": data.get("temp_c", 0),
            "feels_like_c": data.get("feels_like_c", 0),
            "condition": data.get("condition", "unknown"),
            "humidity": data.get("humidity", 0),
            "wind_speed_kmh": data.get("wind_kph", 0),
            "visibility_km": data.get("vis_km", 0),
        }

    def _parse_forecast_day(self, data: Dict) -> WeatherForecast:
        return WeatherForecast(
            date=datetime.fromisoformat(data.get("date", "")),
            condition=WeatherCondition(data.get("condition", "clear")),
            temp_high_c=data.get("max_temp_c", 0),
            temp_low_c=data.get("min_temp_c", 0),
            humidity=data.get("avg_humidity", 0),
            wind_speed_kmh=data.get("max_wind_kph", 0),
            precipitation_mm=data.get("total_precip_mm", 0),
            uv_index=data.get("uv", 0),
            sunrise=data.get("sunrise", ""),
            sunset=data.get("sunset", ""),
        )

    def _calculate_travel_score(self, month_data: Dict) -> float:
        temp = month_data.get("avg_temp_c", 25)
        rain = month_data.get("avg_rain_mm", 50)
        temp_score = max(0, 100 - abs(temp - 25) * 5)
        rain_score = max(0, 100 - rain * 0.5)
        return (temp_score * 0.6 + rain_score * 0.4)

    def _format_recommendation(self, best_months: List[int]) -> str:
        month_names = [
            "", "January", "February", "March", "April", "May",
            "June", "July", "August", "September", "October",
            "November", "December",
        ]
        names = [month_names[m] for m in best_months]
        return f"Best time to visit: {', '.join(names)}"
