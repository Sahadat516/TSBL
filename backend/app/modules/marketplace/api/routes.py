from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.marketplace.application.marketplace_service import MarketplaceService
from app.modules.marketplace.schemas.marketplace_schema import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryTreeResponse,
    CategoryUpdateRequest,
    ProductCreateRequest,
    ProductListResponse,
    ProductResponse,
    ProductUpdateRequest,
    SearchRequest,
)
from app.modules.auth.domain.entities import User

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


def get_marketplace_service(db: AsyncSession = Depends(get_db)) -> MarketplaceService:
    return MarketplaceService(db)


@router.post("/categories", response_model=CategoryResponse, status_code=201)
async def create_category(
    request: CategoryCreateRequest,
    service: MarketplaceService = Depends(get_marketplace_service),
) -> CategoryResponse:
    return await service.create_category(request)


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    request: CategoryUpdateRequest,
    service: MarketplaceService = Depends(get_marketplace_service),
) -> CategoryResponse:
    return await service.update_category(uuid.UUID(category_id), request)


@router.get("/categories/tree", response_model=CategoryTreeResponse)
async def get_category_tree(
    service: MarketplaceService = Depends(get_marketplace_service),
) -> CategoryTreeResponse:
    return await service.get_category_tree()


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    service: MarketplaceService = Depends(get_marketplace_service),
) -> CategoryResponse:
    return await service.get_category(uuid.UUID(category_id))


@router.get("/categories/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(
    slug: str,
    service: MarketplaceService = Depends(get_marketplace_service),
) -> CategoryResponse:
    return await service.get_category_by_slug(slug)


@router.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(
    request: ProductCreateRequest,
    current_user: User = Depends(get_current_user),
    service: MarketplaceService = Depends(get_marketplace_service),
) -> ProductResponse:
    return await service.create_product(current_user.id, request)


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    request: ProductUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: MarketplaceService = Depends(get_marketplace_service),
) -> ProductResponse:
    return await service.update_product(uuid.UUID(product_id), current_user.id, request)


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    service: MarketplaceService = Depends(get_marketplace_service),
) -> ProductResponse:
    return await service.get_product(uuid.UUID(product_id))


@router.get("/products/slug/{slug}", response_model=ProductResponse)
async def get_product_by_slug(
    slug: str,
    service: MarketplaceService = Depends(get_marketplace_service),
) -> ProductResponse:
    return await service.get_product_by_slug(slug)


@router.get("/products", response_model=ProductListResponse)
async def search_products(
    query: str | None = Query(None),
    category_id: str | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    product_type: str | None = Query(None),
    listing_type: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    seller_id: str | None = Query(None),
    is_featured: bool | None = Query(None),
    service: MarketplaceService = Depends(get_marketplace_service),
) -> ProductListResponse:
    search_request = SearchRequest(
        query=query,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        product_type=product_type,
        listing_type=listing_type,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
        seller_id=seller_id,
        is_featured=is_featured,
    )
    return await service.search_products(search_request)


@router.get("/my/products", response_model=ProductListResponse)
async def list_my_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    service: MarketplaceService = Depends(get_marketplace_service),
) -> ProductListResponse:
    return await service.list_seller_products(current_user.id, page, page_size, status)


@router.post("/products/{product_id}/publish", response_model=ProductResponse)
async def publish_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    service: MarketplaceService = Depends(get_marketplace_service),
) -> ProductResponse:
    return await service.publish_product(uuid.UUID(product_id), current_user.id)


@router.post("/products/{product_id}/archive", status_code=200)
async def archive_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    service: MarketplaceService = Depends(get_marketplace_service),
) -> dict:
    await service.archive_product(uuid.UUID(product_id), current_user.id)
    return {"ok": True}
