"""Itinerary planning service for trip management."""
import uuid
from typing import List, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class ActivityType(Enum):
    SIGHTSEEING = "sightseeing"
    DINING = "dining"
    TRANSPORT = "transport"
    ACCOMMODATION = "accommodation"
    ADVENTURE = "adventure"
    SHOPPING = "shopping"
    REST = "rest"
    CULTURAL = "cultural"


@dataclass
class Activity:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    activity_type: ActivityType = ActivityType.SIGHTSEEING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    estimated_cost: float = 0.0
    notes: str = ""
    is_booked: bool = False


@dataclass
class DayPlan:
    day_number: int = 1
    date: Optional[datetime] = None
    activities: List[Activity] = field(default_factory=list)
    notes: str = ""

    @property
    def total_cost(self) -> float:
        return sum(a.estimated_cost for a in self.activities)


@dataclass
class Itinerary:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    title: str = ""
    destination: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    days: List[DayPlan] = field(default_factory=list)
    budget: float = 0.0
    currency: str = "INR"
    shared_with: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def total_days(self) -> int:
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return len(self.days)

    @property
    def total_estimated_cost(self) -> float:
        return sum(day.total_cost for day in self.days)


class ItineraryService:
    """Manages trip itinerary creation and planning."""

    def __init__(self, db_session, recommendation_engine=None):
        self.db = db_session
        self.recommender = recommendation_engine
        self._itineraries: Dict[str, Itinerary] = {}

    async def create_itinerary(
        self,
        user_id: str,
        title: str,
        destination: str,
        start_date: datetime,
        end_date: datetime,
        budget: float = 0.0,
    ) -> Itinerary:
        """Create a new trip itinerary."""
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")

        itinerary = Itinerary(
            user_id=user_id,
            title=title,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
        )

        # Generate empty day plans
        total_days = (end_date - start_date).days + 1
        for i in range(total_days):
            itinerary.days.append(
                DayPlan(
                    day_number=i + 1,
                    date=start_date + timedelta(days=i),
                )
            )

        self._itineraries[itinerary.id] = itinerary
        return itinerary

    async def add_activity(
        self,
        itinerary_id: str,
        day_number: int,
        activity: Activity,
    ) -> Itinerary:
        """Add an activity to a specific day."""
        itinerary = self._itineraries.get(itinerary_id)
        if not itinerary:
            raise ValueError("Itinerary not found")

        if day_number < 1 or day_number > len(itinerary.days):
            raise ValueError(f"Invalid day number: {day_number}")

        day = itinerary.days[day_number - 1]
        day.activities.append(activity)
        day.activities.sort(key=lambda a: a.start_time or datetime.min)

        itinerary.updated_at = datetime.utcnow()
        return itinerary

    async def auto_plan(
        self, itinerary_id: str, preferences: Dict
    ) -> Itinerary:
        """Auto-generate activities using the recommendation engine."""
        itinerary = self._itineraries.get(itinerary_id)
        if not itinerary or not self.recommender:
            raise ValueError("Cannot auto-plan")

        for day in itinerary.days:
            suggestions = await self.recommender.suggest_activities(
                destination=itinerary.destination,
                date=day.date,
                preferences=preferences,
                budget_remaining=itinerary.budget - itinerary.total_estimated_cost,
            )
            day.activities = suggestions

        itinerary.updated_at = datetime.utcnow()
        return itinerary

    async def share_itinerary(
        self, itinerary_id: str, user_ids: List[str]
    ) -> Itinerary:
        """Share itinerary with other users."""
        itinerary = self._itineraries.get(itinerary_id)
        if not itinerary:
            raise ValueError("Itinerary not found")

        itinerary.shared_with.extend(user_ids)
        itinerary.shared_with = list(set(itinerary.shared_with))
        return itinerary

    async def get_budget_summary(self, itinerary_id: str) -> Dict:
        """Get budget breakdown for an itinerary."""
        itinerary = self._itineraries.get(itinerary_id)
        if not itinerary:
            raise ValueError("Itinerary not found")

        by_type: Dict[str, float] = {}
        for day in itinerary.days:
            for activity in day.activities:
                key = activity.activity_type.value
                by_type[key] = by_type.get(key, 0) + activity.estimated_cost

        return {
            "total_budget": itinerary.budget,
            "total_estimated": itinerary.total_estimated_cost,
            "remaining": itinerary.budget - itinerary.total_estimated_cost,
            "by_category": by_type,
            "per_day": [
                {"day": d.day_number, "cost": d.total_cost}
                for d in itinerary.days
            ],
        }
