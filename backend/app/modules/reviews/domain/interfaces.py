from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.modules.reviews.domain.entities import ReviewReply, ReviewVote, SellerReview


class SellerReviewRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> SellerReview | None: ...

    @abstractmethod
    async def list_by_seller(
        self, seller_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[SellerReview], int]: ...

    @abstractmethod
    async def list_by_reviewer(self, reviewer_id: uuid.UUID) -> list[SellerReview]: ...

    @abstractmethod
    async def create(self, entity: SellerReview) -> SellerReview: ...

    @abstractmethod
    async def update(self, entity_id: uuid.UUID, values: dict) -> None: ...


class ReviewReplyRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> ReviewReply | None: ...

    @abstractmethod
    async def list_by_review(self, review_id: uuid.UUID) -> list[ReviewReply]: ...

    @abstractmethod
    async def create(self, entity: ReviewReply) -> ReviewReply: ...

    @abstractmethod
    async def soft_delete(self, entity_id: uuid.UUID) -> None: ...


class ReviewVoteRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_user_and_review(self, user_id: uuid.UUID, review_id: uuid.UUID) -> ReviewVote | None: ...

    @abstractmethod
    async def upsert(self, entity: ReviewVote) -> ReviewVote: ...
