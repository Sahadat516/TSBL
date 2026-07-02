from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")
    description: str | None = None
    icon: str | None = None
    image_url: str | None = None
    parent_id: str | None = None
    sort_order: int = 0


class CategoryUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    slug: str | None = Field(None, min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")
    description: str | None = None
    icon: str | None = None
    image_url: str | None = None
    sort_order: int | None = None
    status: str | None = None


class CategoryResponse(BaseModel):
    id: str
    parent_id: str | None
    name: str
    slug: str
    description: str | None
    icon: str | None
    image_url: str | None
    sort_order: int
    status: str
    level: int
    path: str | None
    children: list[CategoryResponse] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryTreeResponse(BaseModel):
    categories: list[CategoryResponse]


class ProductCreateRequest(BaseModel):
    category_id: str
    title: str = Field(..., min_length=3, max_length=200)
    slug: str = Field(..., min_length=3, max_length=250, pattern=r"^[a-z0-9-]+$")
    description: str = Field(..., min_length=10)
    short_description: str | None = Field(None, max_length=500)
    product_type: str = "digital"
    listing_type: str = "fixed"
    base_price: Decimal = Field(..., gt=0, decimal_places=2)
    compare_at_price: Decimal | None = Field(None, decimal_places=2)
    currency: str = "USD"
    quantity: int = 0
    min_order_quantity: int = 1
    max_order_quantity: int | None = None
    is_digital: bool = False
    has_variants: bool = False
    sku: str | None = None
    tags: list[str] | None = None
    attributes: dict | None = None
    metadata: dict | None = None


class ProductUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=200)
    slug: str | None = Field(None, min_length=3, max_length=250, pattern=r"^[a-z0-9-]+$")
    description: str | None = Field(None, min_length=10)
    short_description: str | None = Field(None, max_length=500)
    category_id: str | None = None
    product_type: str | None = None
    listing_type: str | None = None
    base_price: Decimal | None = Field(None, gt=0, decimal_places=2)
    compare_at_price: Decimal | None = Field(None, decimal_places=2)
    currency: str | None = None
    quantity: int | None = None
    is_digital: bool | None = None
    has_variants: bool | None = None
    sku: str | None = None
    tags: list[str] | None = None
    attributes: dict | None = None
    metadata: dict | None = None
    status: str | None = None


class ProductMediaResponse(BaseModel):
    id: str
    url: str
    thumbnail_url: str | None
    alt_text: str | None
    media_type: str
    sort_order: int
    is_primary: bool

    model_config = {"from_attributes": True}


class ProductVariantResponse(BaseModel):
    id: str
    sku: str | None
    name: str
    price: Decimal
    compare_at_price: Decimal | None
    quantity: int
    options: dict | None
    is_active: bool
    sort_order: int

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id: str
    seller_id: str
    category_id: str
    title: str
    slug: str
    description: str
    short_description: str | None
    product_type: str
    listing_type: str
    status: str
    base_price: Decimal
    compare_at_price: Decimal | None
    currency: str
    quantity: int
    min_order_quantity: int
    max_order_quantity: int | None
    is_featured: bool
    is_active: bool
    is_digital: bool
    has_variants: bool
    sku: str | None
    tags: list[str] | None
    attributes: dict | None
    metadata: dict | None
    total_views: int
    total_sales: int
    average_rating: float
    review_count: int
    media: list[ProductMediaResponse] = []
    variants: list[ProductVariantResponse] = []
    category: CategoryResponse | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProductReviewResponse(BaseModel):
    id: str
    product_id: str
    buyer_id: str
    rating: int
    title: str | None
    content: str | None
    is_verified_purchase: bool
    helpful_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SearchRequest(BaseModel):
    query: str | None = None
    category_id: str | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    product_type: str | None = None
    listing_type: str | None = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    tags: list[str] | None = None
    seller_id: str | None = None
    is_featured: bool | None = None
    status: str = "active"
