from enum import StrEnum


class UserRole(StrEnum):
    GUEST = "guest"
    BUYER = "buyer"
    SELLER = "seller"
    MODERATOR = "moderator"
    SUPPORT = "support"
    FINANCE = "finance"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    DELETED = "deleted"


class AuthMethod(StrEnum):
    EMAIL = "email"
    GOOGLE = "google"
    FACEBOOK = "facebook"
    GITHUB = "github"


class MFAType(StrEnum):
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    NONE = "none"


class OrderStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class DeliveryMethod(StrEnum):
    DOWNLOAD = "download"
    LICENSE_KEY = "license_key"
    EXTERNAL_URL = "external_url"
    EMAIL = "email"


class DeliveryStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"
