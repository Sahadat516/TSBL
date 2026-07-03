from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin, get_current_user
from app.modules.auth.domain.entities import User
from app.modules.reviews.application.review_service import ReviewService
from app.modules.reviews.schemas.review_schema import (
    CreateReviewReplyRequest,
    CreateSellerReviewRequest,
    ModerateReviewRequest,
    ReviewReplyResponse,
    ReviewVoteRequest,
    SellerReviewListResponse,
    SellerReviewResponse,
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


def get_review_service(db: AsyncSession = Depends(get_db)) -> ReviewService:
    return ReviewService(db)


@router.post("/sellers", response_model=SellerReviewResponse, status_code=201)
async def create_seller_review(
    request: CreateSellerReviewRequest,
    current_user: User = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
) -> SellerReviewResponse:
    return await service.create_seller_review(request, current_user.id)


@router.get("/sellers/{seller_id}", response_model=SellerReviewListResponse)
async def list_seller_reviews(
    seller_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: ReviewService = Depends(get_review_service),
) -> SellerReviewListResponse:
    return await service.list_seller_reviews(uuid.UUID(seller_id), page=page, page_size=page_size)


@router.get("/sellers/review/{review_id}", response_model=SellerReviewResponse)
async def get_seller_review(
    review_id: str,
    service: ReviewService = Depends(get_review_service),
) -> SellerReviewResponse:
    return await service.get_seller_review(uuid.UUID(review_id))


@router.post("/replies", response_model=ReviewReplyResponse, status_code=201)
async def add_reply(
    request: CreateReviewReplyRequest,
    current_user: User = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
) -> ReviewReplyResponse:
    return await service.add_reply(request, current_user.id)


@router.post("/vote")
async def vote(
    request: ReviewVoteRequest,
    current_user: User = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
) -> dict:
    return await service.vote(request, current_user.id)


@router.patch("/sellers/{review_id}/moderate", response_model=SellerReviewResponse)
async def moderate_review(
    review_id: str,
    request: ModerateReviewRequest,
    admin: User = Depends(get_current_admin),
    service: ReviewService = Depends(get_review_service),
) -> SellerReviewResponse:
    return await service.moderate_review(uuid.UUID(review_id), request, admin.id)


@router.delete("/sellers/{review_id}", status_code=200)
async def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
) -> dict:
    await service.delete_review(uuid.UUID(review_id), current_user.id)
    return {"ok": True}
