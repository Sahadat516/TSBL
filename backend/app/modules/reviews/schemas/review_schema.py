from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.reviews.domain.value_objects import ReviewStatus, ReviewTargetType, VoteType


class CreateSellerReviewRequest(BaseModel):
    seller_id: UUID
    order_id: UUID | None = None
    rating: int = Field(ge=1, le=5)
    title: str | None = Field(default=None, max_length=200)
    content: str | None = Field(default=None, max_length=5000)
    pros: list[str] | None = None
    cons: list[str] | None = None


class CreateReviewReplyRequest(BaseModel):
    review_type: ReviewTargetType
    review_id: UUID
    content: str = Field(min_length=1, max_length=2000)
    is_seller_response: bool = False


class ReviewVoteRequest(BaseModel):
    review_type: ReviewTargetType
    review_id: UUID
    vote_type: VoteType


class ReviewReplyResponse(BaseModel):
    id: UUID
    review_type: ReviewTargetType
    review_id: UUID
    user_id: UUID
    content: str
    is_seller_response: bool
    is_edited: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SellerReviewResponse(BaseModel):
    id: UUID
    seller_id: UUID
    reviewer_id: UUID
    order_id: UUID | None = None
    rating: int
    title: str | None = None
    content: str | None = None
    pros: dict | None = None
    cons: dict | None = None
    is_verified_purchase: bool
    status: ReviewStatus
    helpful_count: int = 0
    not_helpful_count: int = 0
    replies: list[ReviewReplyResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SellerReviewListResponse(BaseModel):
    items: list[SellerReviewResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    average_rating: float = 0.0


class ModerateReviewRequest(BaseModel):
    status: ReviewStatus = Field(...)
    reason: str | None = Field(default=None, max_length=500)
