from __future__ import annotations

from app.common.base_repository import BaseRepository
from app.modules.admin.domain.entities import AuditLog, SystemConfig


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db) -> None:
        super().__init__(db, AuditLog)


class SystemConfigRepository(BaseRepository[SystemConfig]):
    def __init__(self, db) -> None:
        super().__init__(db, SystemConfig)
