from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from decimal import Decimal

from app.modules.affiliate.domain.entities import AffiliateProfile, Commission, Referral


class AffiliateProfileRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> AffiliateProfile | None: ...

    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> AffiliateProfile | None: ...

    @abstractmethod
    async def get_by_referral_code(self, code: str) -> AffiliateProfile | None: ...

    @abstractmethod
    async def get_or_create(self, user_id: uuid.UUID) -> AffiliateProfile: ...

    @abstractmethod
    async def update(self, entity_id: uuid.UUID, values: dict) -> None: ...


class ReferralRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> Referral | None: ...

    @abstractmethod
    async def list_by_affiliate(self, affiliate_id: uuid.UUID) -> list[Referral]: ...

    @abstractmethod
    async def create(self, entity: Referral) -> Referral: ...

    @abstractmethod
    async def update(self, entity_id: uuid.UUID, values: dict) -> None: ...


class CommissionRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> Commission | None: ...

    @abstractmethod
    async def list_by_affiliate(self, affiliate_id: uuid.UUID) -> list[Commission]: ...

    @abstractmethod
    async def create(self, entity: Commission) -> Commission: ...

    @abstractmethod
    async def update(self, entity_id: uuid.UUID, values: dict) -> None: ...
