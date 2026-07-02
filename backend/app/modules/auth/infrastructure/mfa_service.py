from __future__ import annotations

import base64
import hashlib
import hmac
import struct
import time

from app.modules.auth.domain.interfaces import MFACodeGenerator


class TOTPMFACodeGenerator(MFACodeGenerator):
    def __init__(self, issuer: str = "TSBL Marketplace") -> None:
        self.issuer = issuer

    def generate_secret(self) -> str:
        import pyotp

        return pyotp.random_base32()

    def generate_qr_code_url(self, secret: str, email: str, issuer: str | None = None) -> str:
        import pyotp

        otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name=issuer or self.issuer,
        )
        return otp_uri

    def verify_code(self, secret: str, code: str) -> bool:
        import pyotp

        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)

    def generate_backup_codes(self, count: int = 8) -> list[str]:
        import secrets

        codes: list[str] = []
        for _ in range(count):
            code_bytes = secrets.token_bytes(5)
            code = base64.b32encode(code_bytes).decode("utf-8")[:8].upper()
            code = "-".join([code[:4], code[4:]])
            codes.append(code)
        return codes


class HOTPMFACodeGenerator(MFACodeGenerator):
    def __init__(self, issuer: str = "TSBL Marketplace") -> None:
        self.issuer = issuer

    def generate_secret(self) -> str:
        import pyotp

        return pyotp.random_base32()

    def generate_qr_code_url(self, secret: str, email: str, issuer: str | None = None) -> str:
        import pyotp

        hotp = pyotp.HOTP(secret)
        return hotp.provisioning_uri(name=email, issuer_name=issuer or self.issuer, initial_count=0)

    def verify_code(self, secret: str, code: str) -> bool:
        import pyotp

        hotp = pyotp.HOTP(secret)
        return hotp.verify(code, counter=0)

    def generate_backup_codes(self, count: int = 8) -> list[str]:
        import secrets

        codes: list[str] = []
        for _ in range(count):
            code_bytes = secrets.token_bytes(5)
            code = base64.b32encode(code_bytes).decode("utf-8")[:8].upper()
            code = "-".join([code[:4], code[4:]])
            codes.append(code)
        return codes


def get_mfa_code_generator() -> MFACodeGenerator:
    return TOTPMFACodeGenerator()
