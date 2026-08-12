"""Review and rating service for destinations."""
from typing import List, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class ReviewStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    FLAGGED = "flagged"
    REMOVED = "removed"


@dataclass
class Review:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    destination_id: str = ""
    booking_id: str = ""
    rating: float = 0.0
    title: str = ""
    body: str = ""
    photos: List[str] = field(default_factory=list)
    status: ReviewStatus = ReviewStatus.PENDING
    helpful_votes: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class ReviewService:
    """Manages user reviews and ratings."""

    def __init__(self, db_session):
        self.db = db_session
        self._reviews: Dict[str, Review] = {}

    async def create_review(
        self,
        user_id: str,
        destination_id: str,
        booking_id: str,
        rating: float,
        title: str,
        body: str,
        photos: Optional[List[str]] = None,
    ) -> Review:
        """Submit a new review."""
        if not 1.0 <= rating <= 5.0:
            raise ValueError("Rating must be between 1.0 and 5.0")
        if len(title) < 5:
            raise ValueError("Title must be at least 5 characters")
        if len(body) < 20:
            raise ValueError("Review body must be at least 20 characters")

        review = Review(
            user_id=user_id,
            destination_id=destination_id,
            booking_id=booking_id,
            rating=rating,
            title=title,
            body=body,
            photos=photos or [],
        )

        # Auto-moderate
        if self._check_content(body):
            review.status = ReviewStatus.APPROVED
        else:
            review.status = ReviewStatus.FLAGGED

        self._reviews[review.id] = review
        await self._update_destination_rating(destination_id)
        return review

    async def get_destination_reviews(
        self,
        destination_id: str,
        sort_by: str = "recent",
        page: int = 1,
        per_page: int = 10,
    ) -> Dict:
        """Get reviews for a destination."""
        reviews = [
            r for r in self._reviews.values()
            if r.destination_id == destination_id
            and r.status == ReviewStatus.APPROVED
        ]

        if sort_by == "recent":
            reviews.sort(key=lambda r: r.created_at, reverse=True)
        elif sort_by == "rating_high":
            reviews.sort(key=lambda r: r.rating, reverse=True)
        elif sort_by == "helpful":
            reviews.sort(key=lambda r: r.helpful_votes, reverse=True)

        start = (page - 1) * per_page
        paginated = reviews[start:start + per_page]

        avg_rating = (
            sum(r.rating for r in reviews) / len(reviews)
            if reviews else 0
        )

        return {
            "reviews": paginated,
            "total": len(reviews),
            "average_rating": round(avg_rating, 1),
            "rating_distribution": self._get_distribution(reviews),
        }

    async def vote_helpful(self, review_id: str, user_id: str) -> Review:
        """Mark a review as helpful."""
        review = self._reviews.get(review_id)
        if not review:
            raise ValueError("Review not found")
        review.helpful_votes += 1
        return review

    def _check_content(self, text: str) -> bool:
        """Basic content moderation."""
        flagged_words = ["spam", "fake", "scam"]
        text_lower = text.lower()
        return not any(word in text_lower for word in flagged_words)

    def _get_distribution(self, reviews: List[Review]) -> Dict[int, int]:
        """Get rating distribution."""
        dist = {i: 0 for i in range(1, 6)}
        for r in reviews:
            dist[int(r.rating)] = dist.get(int(r.rating), 0) + 1
        return dist

    async def _update_destination_rating(self, destination_id: str):
        """Update the aggregate rating for a destination."""
        reviews = [
            r for r in self._reviews.values()
            if r.destination_id == destination_id
            and r.status == ReviewStatus.APPROVED
        ]
        if reviews:
            avg = sum(r.rating for r in reviews) / len(reviews)
            await self.db.update_destination_rating(
                destination_id, round(avg, 1), len(reviews)
            )
