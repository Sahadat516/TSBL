from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import AuditLogger
from app.modules.orders.domain.entities import Order
from app.modules.reviews.domain.entities import ReviewReply, ReviewVote, SellerReview
from app.modules.reviews.domain.value_objects import ReviewStatus, ReviewTargetType, VoteType
from app.modules.reviews.infrastructure.review_repository import (
    ReviewReplyRepository,
    ReviewVoteRepository,
    SellerReviewRepository,
)
from app.modules.reviews.schemas.review_schema import (
    CreateReviewReplyRequest,
    CreateSellerReviewRequest,
    ModerateReviewRequest,
    ReviewReplyResponse,
    ReviewVoteRequest,
    SellerReviewListResponse,
    SellerReviewResponse,
    SellerReviewResponse as SellerReviewResp,
)


class ReviewService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.seller_review_repo = SellerReviewRepository(db)
        self.reply_repo = ReviewReplyRepository(db)
        self.vote_repo = ReviewVoteRepository(db)

    async def create_seller_review(
        self, request: CreateSellerReviewRequest, reviewer_id: uuid.UUID
    ) -> SellerReviewResponse:
        if await self.seller_review_repo.has_reviewed(reviewer_id, request.seller_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already reviewed this seller",
            )

        is_verified = False
        if request.order_id:
            result = await self.db.execute(
                select(Order).where(
                    Order.id == request.order_id,
                    Order.seller_id == request.seller_id,
                    Order.buyer_id == reviewer_id,
                    Order.deleted_at.is_(None),
                )
            )
            if result.scalar_one_or_none():
                is_verified = True

        review = SellerReview(
            id=uuid.uuid4(),
            seller_id=request.seller_id,
            reviewer_id=reviewer_id,
            order_id=request.order_id,
            rating=request.rating,
            title=request.title,
            content=request.content,
            pros={"items": request.pros} if request.pros else None,
            cons={"items": request.cons} if request.cons else None,
            is_verified_purchase=is_verified,
            status=ReviewStatus.APPROVED,
        )
        await self.seller_review_repo.create(review)
        await self.db.flush()

        AuditLogger.log(
            action="SELLER_REVIEW_CREATED",
            actor_id=str(reviewer_id),
            resource="seller_review",
            resource_id=str(review.id),
            details={"seller_id": str(request.seller_id), "rating": request.rating},
        )

        return SellerReviewResponse.model_validate(review)

    async def list_seller_reviews(
        self, seller_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> SellerReviewListResponse:
        items, total = await self.seller_review_repo.list_by_seller(
            seller_id, page, page_size, status=ReviewStatus.APPROVED
        )
        avg_rating = await self.seller_review_repo.get_average_rating(seller_id)
        total_pages = max(1, (total + page_size - 1) // page_size)
        return SellerReviewListResponse(
            items=[SellerReviewResponse.model_validate(r) for r in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            average_rating=avg_rating,
        )

    async def get_seller_review(self, review_id: uuid.UUID) -> SellerReviewResponse:
        review = await self.seller_review_repo.get_with_replies(review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
        return SellerReviewResponse.model_validate(review)

    async def add_reply(self, request: CreateReviewReplyRequest, user_id: uuid.UUID) -> ReviewReplyResponse:
        reply = ReviewReply(
            id=uuid.uuid4(),
            review_type=request.review_type,
            review_id=request.review_id,
            seller_review_id=request.review_id if request.review_type == ReviewTargetType.SELLER else None,
            user_id=user_id,
            content=request.content,
            is_seller_response=request.is_seller_response,
        )
        await self.reply_repo.create(reply)
        return ReviewReplyResponse.model_validate(reply)

    async def vote(self, request: ReviewVoteRequest, user_id: uuid.UUID) -> dict:
        vote = ReviewVote(
            id=uuid.uuid4(),
            review_type=request.review_type,
            review_id=request.review_id,
            user_id=user_id,
            vote_type=request.vote_type,
        )
        existing = await self.vote_repo.upsert(vote)

        if request.review_type == ReviewTargetType.SELLER:
            review = await self.seller_review_repo.get(request.review_id)
            if review:
                helpful = await self.db.execute(
                    select(ReviewVote).where(
                        ReviewVote.review_id == request.review_id,
                        ReviewVote.review_type == request.review_type,
                        ReviewVote.vote_type == VoteType.HELPFUL,
                        ReviewVote.deleted_at.is_(None),
                    )
                )
                not_helpful = await self.db.execute(
                    select(ReviewVote).where(
                        ReviewVote.review_id == request.review_id,
                        ReviewVote.review_type == request.review_type,
                        ReviewVote.vote_type == VoteType.NOT_HELPFUL,
                        ReviewVote.deleted_at.is_(None),
                    )
                )
                review.helpful_count = len(helpful.scalars().all())
                review.not_helpful_count = len(not_helpful.scalars().all())
                review.version += 1
                await self.db.flush()

        return {"message": "Vote recorded", "vote_type": request.vote_type.value}

    async def moderate_review(
        self, review_id: uuid.UUID, request: ModerateReviewRequest, moderator_id: uuid.UUID
    ) -> SellerReviewResponse:
        review = await self.seller_review_repo.get(review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

        review.status = request.status
        review.moderated_by = moderator_id
        review.moderated_at = datetime.now(timezone.utc)
        review.moderation_reason = request.reason
        review.version += 1
        await self.db.flush()

        AuditLogger.log(
            action="REVIEW_MODERATED",
            actor_id=str(moderator_id),
            resource="seller_review",
            resource_id=str(review.id),
            details={"new_status": request.status.value},
        )

        return SellerReviewResponse.model_validate(review)

    async def delete_review(self, review_id: uuid.UUID, user_id: uuid.UUID) -> None:
        review = await self.seller_review_repo.get(review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
        if review.reviewer_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your review")
        await self.seller_review_repo.soft_delete(review_id)
