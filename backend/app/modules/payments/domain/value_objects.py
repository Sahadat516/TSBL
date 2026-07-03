from __future__ import annotations

from enum import StrEnum


class PaymentGateway(StrEnum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    RAZORPAY = "razorpay"
    SSLCOMMERZ = "sslcommerz"
    BKASH = "bkash"
    NAGAD = "nagad"
    ROCKET = "rocket"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"


class TransactionStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentMethodType(StrEnum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_ACCOUNT = "bank_account"
    MOBILE_BANKING = "mobile_banking"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTO = "crypto"


class PayoutStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    HOLD = "hold"
    CANCELLED = "cancelled"


class RefundReason(StrEnum):
    ORDER_CANCELLED = "order_cancelled"
    ITEM_NOT_AS_DESCRIBED = "item_not_as_described"
    ITEM_NOT_RECEIVED = "item_not_received"
    DUPLICATE_PAYMENT = "duplicate_payment"
    FRAUD_SUSPECTED = "fraud_suspected"
    CUSTOMER_REQUEST = "customer_request"
    SELLER_AGREED = "seller_agreed"
    OTHER = "other"


class Currency(StrEnum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    BDT = "BDT"
    INR = "INR"
    SGD = "SGD"
    MYR = "MYR"
