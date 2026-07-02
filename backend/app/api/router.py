from fastapi import APIRouter

from app.api.health import router as health_router
from app.modules.auth.api.routes import router as auth_router
from app.modules.marketplace.api.routes import router as marketplace_router
from app.modules.orders.api.routes import router as orders_router
from app.modules.authorization.api.routes import router as authz_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(marketplace_router)
api_router.include_router(orders_router)
api_router.include_router(authz_router)
