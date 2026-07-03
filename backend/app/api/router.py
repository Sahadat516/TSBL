from fastapi import APIRouter

from app.api.health import router as health_router
from app.modules.auth.api.routes import router as auth_router
from app.modules.marketplace.api.routes import router as marketplace_router
from app.modules.orders.api.routes import router as orders_router
from app.modules.authorization.api.routes import router as authz_router
from app.modules.admin.api.routes import router as admin_router
from app.modules.affiliate.api.routes import router as affiliate_router
from app.modules.analytics.api.routes import router as analytics_router
from app.modules.chat.api.routes import router as chat_router
from app.modules.escrow.api.routes import router as escrow_router
from app.modules.notifications.api.routes import router as notifications_router
from app.modules.payments.api.routes import router as payments_router
from app.modules.reviews.api.routes import router as reviews_router
from app.modules.support.api.routes import router as support_router
from app.modules.wallet.api.routes import router as wallet_router
from app.modules.user.api.routes import router as user_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(admin_router)
api_router.include_router(affiliate_router)
api_router.include_router(analytics_router)
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(escrow_router)
api_router.include_router(marketplace_router)
api_router.include_router(notifications_router)
api_router.include_router(orders_router)
api_router.include_router(authz_router)
api_router.include_router(payments_router)
api_router.include_router(reviews_router)
api_router.include_router(support_router)
api_router.include_router(wallet_router)
api_router.include_router(user_router)
