from __future__ import annotations

from app.modules.admin.domain.exceptions import (
    AdminDomainError,
    AuditLogNotFoundError,
    SystemConfigKeyError,
    SystemConfigNotFoundError,
)


class TestAdminExceptions:
    def test_hierarchy(self):
        assert issubclass(AuditLogNotFoundError, AdminDomainError)

    def test_status_codes(self):
        assert AuditLogNotFoundError.status_code == 404
        assert SystemConfigNotFoundError.status_code == 404
        assert SystemConfigKeyError.status_code == 422

    def test_error_codes(self):
        assert AuditLogNotFoundError.code == "audit_log_not_found"
        assert SystemConfigNotFoundError.code == "system_config_not_found"
        assert SystemConfigKeyError.code == "system_config_key_error"
        assert AdminDomainError.code == "admin_error"
