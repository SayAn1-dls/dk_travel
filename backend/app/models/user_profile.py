"""User profile and travel preferences models."""
from typing import List, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TravelStyle(Enum):
    BUDGET = "budget"
    COMFORT = "comfort"
    LUXURY = "luxury"
    BACKPACKER = "backpacker"


class DietPreference(Enum):
    NONE = "none"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    HALAL = "halal"
    KOSHER = "kosher"
    GLUTEN_FREE = "gluten_free"


@dataclass
class TravelPreferences:
    travel_style: TravelStyle = TravelStyle.COMFORT
    preferred_activities: List[str] = field(default_factory=list)
    diet: DietPreference = DietPreference.NONE
    accessibility_needs: List[str] = field(default_factory=list)
    preferred_languages: List[str] = field(default_factory=lambda: ["en", "hi"])
    max_flight_hours: int = 12
    preferred_accommodation: str = "hotel"
    interests: List[str] = field(default_factory=list)


@dataclass
class EmergencyContact:
    name: str = ""
    phone: str = ""
    relationship: str = ""
    email: str = ""


@dataclass
class UserProfile:
    user_id: str = ""
    display_name: str = ""
    email: str = ""
    phone: str = ""
    avatar_url: str = ""
    bio: str = ""
    location: str = ""
    date_of_birth: Optional[datetime] = None
    passport_country: str = ""
    preferences: TravelPreferences = field(default_factory=TravelPreferences)
    emergency_contact: Optional[EmergencyContact] = None
    favorite_destinations: List[str] = field(default_factory=list)
    visited_destinations: List[str] = field(default_factory=list)
    badges: List[str] = field(default_factory=list)
    member_since: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    is_verified: bool = False
    notification_settings: Dict = field(default_factory=lambda: {
        "email_booking": True,
        "email_promotions": False,
        "push_reminders": True,
        "sms_alerts": True,
    })

    @property
    def trips_count(self) -> int:
        return len(self.visited_destinations)

    @property
    def travel_level(self) -> str:
        count = self.trips_count
        if count >= 20:
            return "Globe Trotter"
        elif count >= 10:
            return "Explorer"
        elif count >= 5:
            return "Adventurer"
        elif count >= 1:
            return "Traveler"
        return "Newcomer"

    def add_badge(self, badge: str):
        if badge not in self.badges:
            self.badges.append(badge)

    def update_activity(self):
        self.last_active = datetime.utcnow()
