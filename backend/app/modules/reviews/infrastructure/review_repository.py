from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.base_repository import BaseRepository
from app.modules.reviews.domain.entities import ReviewReply, ReviewVote, SellerReview
from app.modules.reviews.domain.value_objects import ReviewStatus


class SellerReviewRepository(BaseRepository[SellerReview]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, SellerReview)

    async def get_with_replies(self, review_id: uuid.UUID) -> SellerReview | None:
        result = await self.db.execute(
            select(SellerReview)
            .where(SellerReview.id == review_id, SellerReview.deleted_at.is_(None))
            .options(selectinload(SellerReview.replies))
        )
        return result.scalar_one_or_none()

    async def list_by_seller(
        self, seller_id: uuid.UUID, page: int = 1, page_size: int = 20, status: ReviewStatus | None = None
    ) -> tuple[list[SellerReview], int]:
        query = select(SellerReview).where(
            SellerReview.seller_id == seller_id,
            SellerReview.deleted_at.is_(None),
        )
        if status:
            query = query.where(SellerReview.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        if total == 0:
            return [], 0

        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(SellerReview.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .options(selectinload(SellerReview.replies))
        )
        items = list(result.unique().scalars().all())
        return items, total

    async def get_average_rating(self, seller_id: uuid.UUID) -> float:
        result = await self.db.execute(
            select(func.avg(SellerReview.rating)).where(
                SellerReview.seller_id == seller_id,
                SellerReview.status == ReviewStatus.APPROVED,
                SellerReview.deleted_at.is_(None),
            )
        )
        avg = result.scalar()
        return float(avg) if avg else 0.0

    async def has_reviewed(self, reviewer_id: uuid.UUID, seller_id: uuid.UUID) -> bool:
        result = await self.db.execute(
            select(func.count(SellerReview.id)).where(
                SellerReview.reviewer_id == reviewer_id,
                SellerReview.seller_id == seller_id,
                SellerReview.deleted_at.is_(None),
            )
        )
        return (result.scalar() or 0) > 0


class ReviewReplyRepository(BaseRepository[ReviewReply]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, ReviewReply)

    async def list_by_review(self, review_type: str, review_id: uuid.UUID) -> list[ReviewReply]:
        result = await self.db.execute(
            select(ReviewReply)
            .where(
                ReviewReply.review_type == review_type,
                ReviewReply.review_id == review_id,
                ReviewReply.deleted_at.is_(None),
            )
            .order_by(ReviewReply.created_at.asc())
        )
        return list(result.scalars().all())


class ReviewVoteRepository(BaseRepository[ReviewVote]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, ReviewVote)

    async def get_by_user_and_review(self, user_id: uuid.UUID, review_type: str, review_id: uuid.UUID) -> ReviewVote | None:
        result = await self.db.execute(
            select(ReviewVote).where(
                ReviewVote.user_id == user_id,
                ReviewVote.review_type == review_type,
                ReviewVote.review_id == review_id,
                ReviewVote.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def upsert(self, entity: ReviewVote) -> ReviewVote:
        existing = await self.get_by_user_and_review(entity.user_id, entity.review_type.value, entity.review_id)
        if existing:
            existing.vote_type = entity.vote_type
            existing.version += 1
            await self.db.flush()
            return existing
        self.db.add(entity)
        await self.db.flush()
        return entity
