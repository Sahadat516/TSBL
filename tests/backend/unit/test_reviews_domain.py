from __future__ import annotations

import pytest

from app.modules.reviews.domain.value_objects import ModerationStatus, VoteType


class TestVoteType:
    def test_values(self):
        assert VoteType.HELPFUL == "helpful"
        assert VoteType.NOT_HELPFUL == "not_helpful"


class TestModerationStatus:
    def test_values(self):
        assert ModerationStatus.PENDING == "pending"
        assert ModerationStatus.APPROVED == "approved"
        assert ModerationStatus.REJECTED == "rejected"
        assert ModerationStatus.FLAGGED == "flagged"
