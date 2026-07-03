from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import UserRole, UserStatus
from app.core.logging import AuditLogger
from app.modules.admin.domain.entities import AuditLog as AdminAuditLog, SystemConfig
from app.modules.admin.domain.value_objects import AuditAction
from app.modules.admin.infrastructure.admin_repository import AuditLogRepository, SystemConfigRepository
from app.modules.admin.schemas.admin_schema import (
    AdminDashboardResponse,
    AdminUserActionRequest,
    AuditLogListResponse,
    AuditLogResponse,
    SystemConfigResponse,
    UpdateSystemConfigRequest,
)
from app.modules.auth.domain.entities import User
from app.modules.escrow.domain.entities import Dispute
from app.modules.escrow.domain.value_objects import DisputeStatus
from app.modules.marketplace.domain.entities import Product
from app.modules.orders.domain.entities import Order
from app.modules.payments.domain.entities import Payout
from app.modules.payments.domain.value_objects import PayoutStatus
from app.modules.support.domain.entities import Ticket


class AdminService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.audit_repo = AuditLogRepository(db)
        self.config_repo = SystemConfigRepository(db)

    async def get_dashboard(self) -> AdminDashboardResponse:
        user_count = await self.db.execute(select(func.count(User.id)).where(User.deleted_at.is_(None)))
        seller_count = await self.db.execute(
            select(func.count(User.id)).where(User.role == UserRole.SELLER, User.deleted_at.is_(None))
        )
        product_count = await self.db.execute(select(func.count(Product.id)).where(Product.deleted_at.is_(None)))
        order_count = await self.db.execute(select(func.count(Order.id)).where(Order.deleted_at.is_(None)))
        pending_products = await self.db.execute(
            select(func.count(Product.id)).where(Product.status == "pending", Product.deleted_at.is_(None))
        )
        open_disputes = await self.db.execute(
            select(func.count(Dispute.id)).where(Dispute.status.in_([DisputeStatus.OPEN, DisputeStatus.UNDER_REVIEW]))
        )
        pending_payouts = await self.db.execute(
            select(func.count(Payout.id)).where(Payout.status == PayoutStatus.PENDING)
        )
        open_tickets = await self.db.execute(
            select(func.count(Ticket.id)).where(Ticket.status.in_(["open", "pending", "in_progress"]), Ticket.deleted_at.is_(None))
        )

        recent_result = await self.db.execute(
            select(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(10)
        )

        return AdminDashboardResponse(
            total_users=user_count.scalar() or 0,
            total_sellers=seller_count.scalar() or 0,
            total_products=product_count.scalar() or 0,
            total_orders=order_count.scalar() or 0,
            pending_products=pending_products.scalar() or 0,
            open_disputes=open_disputes.scalar() or 0,
            pending_payouts=pending_payouts.scalar() or 0,
            open_tickets=open_tickets.scalar() or 0,
            recent_actions=[AuditLogResponse.model_validate(a) for a in recent_result.scalars().all()],
        )

    async def suspend_user(self, request: AdminUserActionRequest, admin_id: uuid.UUID) -> dict:
        user = await self.db.get(User, request.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.status = UserStatus.SUSPENDED
        user.updated_at = datetime.now(timezone.utc)
        await self.db.flush()

        await self._log_audit(admin_id, AuditAction.USER_SUSPENDED, "user", str(request.user_id), {"reason": request.reason})
        return {"message": "User suspended", "user_id": str(request.user_id)}

    async def ban_user(self, request: AdminUserActionRequest, admin_id: uuid.UUID) -> dict:
        user = await self.db.get(User, request.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.status = UserStatus.BANNED
        user.updated_at = datetime.now(timezone.utc)
        await self.db.flush()

        await self._log_audit(admin_id, AuditAction.USER_BANNED, "user", str(request.user_id), {"reason": request.reason})
        return {"message": "User banned", "user_id": str(request.user_id)}

    async def approve_product(self, product_id: uuid.UUID, admin_id: uuid.UUID) -> dict:
        product = await self.db.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        product.status = "active"
        product.is_active = True
        product.approved_at = datetime.now(timezone.utc)
        await self.db.flush()

        await self._log_audit(admin_id, AuditAction.PRODUCT_APPROVED, "product", str(product_id))
        return {"message": "Product approved", "product_id": str(product_id)}

    async def get_audit_logs(self, page: int = 1, page_size: int = 50) -> AuditLogListResponse:
        query = select(AdminAuditLog).where(AdminAuditLog.deleted_at.is_(None))
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(AdminAuditLog.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        total_pages = max(1, (total + page_size - 1) // page_size)
        return AuditLogListResponse(
            items=[AuditLogResponse.model_validate(a) for a in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_config(self, key: str) -> SystemConfigResponse:
        result = await self.db.execute(
            select(SystemConfig).where(SystemConfig.key == key, SystemConfig.deleted_at.is_(None))
        )
        config = result.scalar_one_or_none()
        if not config:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
        return SystemConfigResponse.model_validate(config)

    async def update_config(self, key: str, request: UpdateSystemConfigRequest, admin_id: uuid.UUID) -> SystemConfigResponse:
        result = await self.db.execute(
            select(SystemConfig).where(SystemConfig.key == key, SystemConfig.deleted_at.is_(None))
        )
        config = result.scalar_one_or_none()
        if not config:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
        config.value = request.value
        if request.description is not None:
            config.description = request.description
        if request.is_public is not None:
            config.is_public = request.is_public
        config.updated_by = admin_id
        config.version += 1
        await self.db.flush()
        return SystemConfigResponse.model_validate(config)

    async def _log_audit(
        self, admin_id: uuid.UUID, action: AuditAction, resource_type: str,
        resource_id: str | None = None, details: dict | None = None
    ) -> None:
        log = AdminAuditLog(
            id=uuid.uuid4(),
            admin_id=admin_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
        )
        await self.audit_repo.create(log)
        await self.db.flush()
