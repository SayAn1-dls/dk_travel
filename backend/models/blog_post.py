"""Blog post data model and schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BlogAuthor(BaseModel):
    """Blog post author."""
    user_id: str = Field(..., description="Author user ID")
    name: str = Field(..., description="Author display name")
    bio: str = Field(default="", description="Short bio")
    avatar: str = Field(default="", description="Avatar URL")


class BlogPost(BaseModel):
    """Full blog post document model."""
    id: Optional[str] = Field(None, alias="_id")
    title: str = Field(..., min_length=1, max_length=300, description="Post title")
    slug: str = Field(default="", max_length=300, description="URL slug")
    excerpt: str = Field(default="", max_length=500, description="Short excerpt")
    content: str = Field(..., min_length=50, description="Full post content (Markdown)")
    author: BlogAuthor
    category: str = Field(default="General", description="Post category")
    tags: List[str] = Field(default_factory=list, description="Post tags")
    cover_image: str = Field(default="", description="Cover image URL")
    images: List[str] = Field(default_factory=list, description="In-post image URLs")
    destination: str = Field(default="", description="Related destination")
    country: str = Field(default="", description="Country")
    read_time_minutes: int = Field(default=5, ge=1, description="Estimated read time")
    views: int = Field(default=0, ge=0, description="View count")
    likes: int = Field(default=0, ge=0, description="Like count")
    is_featured: bool = Field(default=False, description="Featured post")
    is_published: bool = Field(default=False, description="Published status")
    published_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class BlogPostCreate(BaseModel):
    """Schema for creating a new blog post."""
    title: str = Field(..., min_length=1, max_length=300)
    content: str = Field(..., min_length=50)
    excerpt: str = Field(default="", max_length=500)
    category: str = Field(default="General")
    tags: List[str] = Field(default_factory=list)
    cover_image: str = Field(default="")
    destination: str = Field(default="")
    country: str = Field(default="")
    is_published: bool = Field(default=False)


class BlogPostResponse(BaseModel):
    """Blog post API response."""
    id: str
    title: str
    slug: str
    excerpt: str
    content: str
    author: BlogAuthor
    category: str
    tags: List[str]
    cover_image: str
    destination: str
    country: str
    read_time_minutes: int
    views: int
    likes: int
    is_featured: bool
    published_at: Optional[str]
    created_at: str


class BlogPostList(BaseModel):
    """Paginated blog post list response."""
    posts: List[BlogPostResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
