from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import AuditLogger
from app.modules.marketplace.domain.entities import Product, ProductStatus, ProductType
from app.modules.marketplace.infrastructure.marketplace_repository import (
    CategoryRepository,
    ProductRepository,
)
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


class MarketplaceService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.category_repo = CategoryRepository(db)
        self.product_repo = ProductRepository(db)

    async def create_category(self, request: CategoryCreateRequest) -> CategoryResponse:
        existing = await self.category_repo.find_by_slug(request.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Category slug already exists"
            )

        parent_id = uuid.UUID(request.parent_id) if request.parent_id else None
        level = 0
        path = request.slug

        if parent_id:
            parent = await self.category_repo.get(parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Parent category not found"
                )
            level = parent.level + 1
            path = f"{parent.path}/{request.slug}" if parent.path else request.slug

        category = Category(
            id=uuid.uuid4(),
            parent_id=parent_id,
            name=request.name,
            slug=request.slug,
            description=request.description,
            icon=request.icon,
            image_url=request.image_url,
            sort_order=request.sort_order,
            level=level,
            path=path,
        )
        await self.category_repo.create(category)

        AuditLogger.log(
            action="CATEGORY_CREATED",
            actor_id="system",
            resource="category",
            resource_id=str(category.id),
            details={"name": request.name, "slug": request.slug},
        )

        return CategoryResponse.model_validate(category)

    async def update_category(
        self, category_id: uuid.UUID, request: CategoryUpdateRequest
    ) -> CategoryResponse:
        category = await self.category_repo.get(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        if request.slug is not None and request.slug != category.slug:
            existing = await self.category_repo.find_by_slug(request.slug)
            if existing and existing.id != category_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="Category slug already in use"
                )

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(category, field):
                setattr(category, field, value)

        await self.db.flush()
        return CategoryResponse.model_validate(category)

    async def get_category_tree(self) -> CategoryTreeResponse:
        categories = await self.category_repo.find_active()
        tree = self._build_tree(categories)
        return CategoryTreeResponse(categories=tree)

    async def get_category(self, category_id: uuid.UUID) -> CategoryResponse:
        category = await self.category_repo.get(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        children = await self.category_repo.find_children(category_id)
        response = CategoryResponse.model_validate(category)
        if children:
            response.children = [CategoryResponse.model_validate(c) for c in children]
        return response

    async def get_category_by_slug(self, slug: str) -> CategoryResponse:
        category = await self.category_repo.find_by_slug(slug)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        return CategoryResponse.model_validate(category)

    async def create_product(
        self, seller_id: uuid.UUID, request: ProductCreateRequest
    ) -> ProductResponse:
        existing = await self.product_repo.find_by_slug(request.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Product slug already exists"
            )

        category = await self.category_repo.get(uuid.UUID(request.category_id))
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        product = Product(
            id=uuid.uuid4(),
            seller_id=seller_id,
            category_id=uuid.UUID(request.category_id),
            title=request.title,
            slug=request.slug,
            description=request.description,
            short_description=request.short_description,
            product_type=ProductType(request.product_type),
            listing_type=request.listing_type,
            base_price=request.base_price,
            compare_at_price=request.compare_at_price,
            currency=request.currency,
            quantity=request.quantity,
            min_order_quantity=request.min_order_quantity,
            max_order_quantity=request.max_order_quantity,
            is_digital=request.is_digital,
            has_variants=request.has_variants,
            sku=request.sku,
            tags=request.tags,
            attributes=request.attributes,
            metadata=request.metadata,
        )
        await self.product_repo.create(product)

        AuditLogger.log(
            action="PRODUCT_CREATED",
            actor_id=str(seller_id),
            resource="product",
            resource_id=str(product.id),
            details={"title": request.title, "slug": request.slug},
        )

        return await self._load_product_response(product.id)

    async def update_product(
        self, product_id: uuid.UUID, seller_id: uuid.UUID, request: ProductUpdateRequest
    ) -> ProductResponse:
        product = await self.product_repo.get(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        if product.seller_id != seller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not your product"
            )

        if request.slug and request.slug != product.slug:
            existing = await self.product_repo.find_by_slug(request.slug)
            if existing and existing.id != product_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="Product slug already in use"
                )

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(product, field) and value is not None:
                setattr(product, field, value)

        if request.category_id:
            product.category_id = uuid.UUID(request.category_id)

        if request.tags is not None:
            product.tags = {"items": request.tags} if request.tags else None

        await self.db.flush()
        return await self._load_product_response(product_id)

    async def get_product(self, product_id: uuid.UUID) -> ProductResponse:
        product = await self._load_product_response(product_id)
        await self.product_repo.increment_views(product_id)
        return product

    async def get_product_by_slug(self, slug: str) -> ProductResponse:
        product = await self.product_repo.find_by_slug(slug)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        return ProductResponse.model_validate(product)

    async def list_seller_products(
        self,
        seller_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> ProductListResponse:
        products, total = await self.product_repo.find_by_seller(
            seller_id, page, page_size, status
        )
        return ProductListResponse(
            products=[ProductResponse.model_validate(p) for p in products],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=max(1, (total + page_size - 1) // page_size),
        )

    async def search_products(self, request: SearchRequest) -> ProductListResponse:
        products, total = await self.product_repo.search(
            query=request.query,
            category_id=uuid.UUID(request.category_id) if request.category_id else None,
            min_price=request.min_price,
            max_price=request.max_price,
            product_type=request.product_type,
            listing_type=request.listing_type,
            seller_id=uuid.UUID(request.seller_id) if request.seller_id else None,
            is_featured=request.is_featured,
            tags=request.tags,
            sort_by=request.sort_by,
            sort_order=request.sort_order,
            page=request.page,
            page_size=request.page_size,
        )
        return ProductListResponse(
            products=[ProductResponse.model_validate(p) for p in products],
            total=total,
            page=request.page,
            page_size=request.page_size,
            total_pages=max(1, (total + request.page_size - 1) // request.page_size),
        )

    async def publish_product(self, product_id: uuid.UUID, seller_id: uuid.UUID) -> ProductResponse:
        product = await self.product_repo.get(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        if product.seller_id != seller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not your product"
            )

        product.status = ProductStatus.ACTIVE
        product.is_active = True
        product.published_at = datetime.now(timezone.utc)
        await self.db.flush()

        return await self._load_product_response(product_id)

    async def archive_product(self, product_id: uuid.UUID, seller_id: uuid.UUID) -> None:
        product = await self.product_repo.get(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        if product.seller_id != seller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not your product"
            )
        product.status = ProductStatus.ARCHIVED
        product.is_active = False
        await self.db.flush()

    async def _load_product_response(self, product_id: uuid.UUID) -> ProductResponse:
        product = await self.product_repo.get(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        loaded = await self.product_repo.find_by_slug(product.slug)
        return ProductResponse.model_validate(loaded or product)
