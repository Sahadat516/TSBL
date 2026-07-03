from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.modules.reviews.domain.value_objects import ModerationStatus, VoteType
from app.modules.reviews.schemas.review_schema import (
    CreateReviewRequest,
    ModerateReviewRequest,
    ReviewResponse,
    ReviewVoteResponse,
    VoteReviewRequest,
)


class TestCreateReviewRequest:
    def test_valid(self):
        req = CreateReviewRequest(
            seller_id=uuid.uuid4(),
            rating=5,
            title="Great seller",
            content="Very professional",
            pros="Fast shipping",
            cons="None",
        )
        assert req.rating == 5
        assert req.title == "Great seller"

    def test_invalid_rating_low(self):
        with pytest.raises(ValidationError):
            CreateReviewRequest(
                seller_id=uuid.uuid4(),
                rating=0,
                content="OK",
            )

    def test_invalid_rating_high(self):
        with pytest.raises(ValidationError):
            CreateReviewRequest(
                seller_id=uuid.uuid4(),
                rating=6,
                content="OK",
            )

    def test_empty_content_raises(self):
        with pytest.raises(ValidationError):
            CreateReviewRequest(
                seller_id=uuid.uuid4(),
                rating=3,
                content="",
            )


class TestVoteReviewRequest:
    def test_valid(self):
        req = VoteReviewRequest(vote=VoteType.HELPFUL)
        assert req.vote == VoteType.HELPFUL

    def test_invalid_vote(self):
        with pytest.raises(ValidationError):
            VoteReviewRequest(vote="invalid")


class TestModerateReviewRequest:
    def test_valid(self):
        req = ModerateReviewRequest(
            status=ModerationStatus.APPROVED,
            moderation_note="Looks good",
        )
        assert req.status == ModerationStatus.APPROVED

    def test_default_note(self):
        req = ModerateReviewRequest(status=ModerationStatus.REJECTED)
        assert req.moderation_note is None


class TestReviewResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = ReviewResponse(
            id=uuid.uuid4(),
            reviewer_id=uuid.uuid4(),
            seller_id=uuid.uuid4(),
            rating=5,
            content="Excellent seller",
            moderation_status=ModerationStatus.APPROVED,
            is_verified_purchase=True,
            created_at=now,
            updated_at=now,
        )
        assert resp.rating == 5
        assert resp.is_verified_purchase is True
        assert resp.moderation_status == ModerationStatus.APPROVED

    def test_from_attributes(self):
        assert ReviewResponse.model_config.get("from_attributes") is True


class TestReviewVoteResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = ReviewVoteResponse(
            id=uuid.uuid4(),
            review_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            vote=VoteType.HELPFUL,
            created_at=now,
        )
        assert resp.vote == VoteType.HELPFUL

    def test_from_attributes(self):
        assert ReviewVoteResponse.model_config.get("from_attributes") is True
