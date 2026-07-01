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
