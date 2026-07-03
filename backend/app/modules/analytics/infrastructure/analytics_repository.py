from __future__ import annotations

from app.common.base_repository import BaseRepository
from app.modules.analytics.domain.entities import SavedReport


class SavedReportRepository(BaseRepository[SavedReport]):
    def __init__(self, db) -> None:
        super().__init__(db, SavedReport)
