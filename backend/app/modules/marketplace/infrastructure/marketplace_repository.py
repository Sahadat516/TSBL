from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.common.base_repository import BaseRepository
from app.modules.marketplace.domain.entities import (
    Category,
    Product,
    ProductMedia,
    ProductReview,
    ProductStatus,
    ProductVariant,
)


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Category)

    async def find_by_slug(self, slug: str) -> Category | None:
        result = await self.db.execute(
            select(Category).where(Category.slug == slug, Category.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def find_active(self) -> list[Category]:
        result = await self.db.execute(
            select(Category)
            .where(Category.status == "active", Category.deleted_at.is_(None))
            .order_by(Category.sort_order, Category.name)
        )
        return list(result.scalars().all())

    async def find_root_categories(self) -> list[Category]:
        result = await self.db.execute(
            select(Category)
            .where(Category.parent_id.is_(None), Category.deleted_at.is_(None))
            .order_by(Category.sort_order)
        )
        return list(result.scalars().all())

    async def find_children(self, parent_id: uuid.UUID) -> list[Category]:
        result = await self.db.execute(
            select(Category)
            .where(Category.parent_id == parent_id, Category.deleted_at.is_(None))
            .order_by(Category.sort_order)
        )
        return list(result.scalars().all())


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Product)

    async def find_by_slug(self, slug: str) -> Product | None:
        result = await self.db.execute(
            select(Product)
            .options(
                selectinload(Product.media),
                selectinload(Product.variants),
                joinedload(Product.category),
            )
            .where(Product.slug == slug, Product.deleted_at.is_(None))
        )
        return result.unique().scalar_one_or_none()

    async def find_by_seller(
        self, seller_id: uuid.UUID, page: int = 1, page_size: int = 20, status: str | None = None
    ) -> tuple[list[Product], int]:
        query = select(Product).where(
            Product.seller_id == seller_id, Product.deleted_at.is_(None)
        )
        count_query = select(Product.id).where(
            Product.seller_id == seller_id, Product.deleted_at.is_(None)
        )

        if status:
            query = query.where(Product.status == status)
            count_query = count_query.where(Product.status == status)

        total_result = await self.db.execute(count_query)
        total = len(total_result.scalars().all())

        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(Product.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .options(
                selectinload(Product.media),
                joinedload(Product.category),
            )
        )
        products = list(result.unique().scalars().all())
        return products, total

    async def search(
        self,
        query: str | None = None,
        category_id: uuid.UUID | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        product_type: str | None = None,
        listing_type: str | None = None,
        seller_id: uuid.UUID | None = None,
        is_featured: bool | None = None,
        tags: list[str] | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Product], int]:
        base_query = select(Product).where(
            Product.status == ProductStatus.ACTIVE,
            Product.deleted_at.is_(None),
        )
        count_query = select(Product.id).where(
            Product.status == ProductStatus.ACTIVE,
            Product.deleted_at.is_(None),
        )

        if query:
            pattern = f"%{query}%"
            filter_clause = or_(
                Product.title.ilike(pattern),
                Product.description.ilike(pattern),
                Product.short_description.ilike(pattern),
                Product.tags["name"].as_string().ilike(pattern),
            )
            base_query = base_query.where(filter_clause)
            count_query = count_query.where(filter_clause)

        if category_id:
            base_query = base_query.where(Product.category_id == category_id)
            count_query = count_query.where(Product.category_id == category_id)

        if min_price is not None:
            base_query = base_query.where(Product.base_price >= min_price)
            count_query = count_query.where(Product.base_price >= min_price)

        if max_price is not None:
            base_query = base_query.where(Product.base_price <= max_price)
            count_query = count_query.where(Product.base_price <= max_price)

        if product_type:
            base_query = base_query.where(Product.product_type == product_type)
            count_query = count_query.where(Product.product_type == product_type)

        if listing_type:
            base_query = base_query.where(Product.listing_type == listing_type)
            count_query = count_query.where(Product.listing_type == listing_type)

        if seller_id:
            base_query = base_query.where(Product.seller_id == seller_id)
            count_query = count_query.where(Product.seller_id == seller_id)

        if is_featured is not None:
            base_query = base_query.where(Product.is_featured == is_featured)
            count_query = count_query.where(Product.is_featured == is_featured)

        if tags:
            base_query = base_query.where(Product.tags.has_any(tags))
            count_query = count_query.where(Product.tags.has_any(tags))

        total_result = await self.db.execute(count_query)
        total = len(total_result.scalars().all())

        sort_column = getattr(Product, sort_by, Product.created_at)
        order_fn = sort_column.desc() if sort_order == "desc" else sort_column.asc()
        offset = (page - 1) * page_size

        result = await self.db.execute(
            base_query.order_by(order_fn)
            .offset(offset)
            .limit(page_size)
            .options(
                selectinload(Product.media),
                selectinload(Product.variants),
                joinedload(Product.category),
            )
        )
        products = list(result.unique().scalars().all())
        return products, total

    async def increment_views(self, product_id: uuid.UUID) -> None:
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .execution_options(synchronize_session=False)
        )
        result = await self.db.execute(stmt)
        product = result.scalar_one_or_none()
        if product:
            product.total_views = Product.total_views + 1
            await self.db.flush()


class ProductMediaRepository(BaseRepository[ProductMedia]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, ProductMedia)


class ProductVariantRepository(BaseRepository[ProductVariant]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, ProductVariant)

    async def find_by_product(self, product_id: uuid.UUID) -> list[ProductVariant]:
        result = await self.db.execute(
            select(ProductVariant)
            .where(
                ProductVariant.product_id == product_id,
                ProductVariant.deleted_at.is_(None),
            )
            .order_by(ProductVariant.sort_order)
        )
        return list(result.scalars().all())
