from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from app.core.config import Settings


class TestSettings:
    def test_default_values(self):
        settings = Settings()
        assert settings.app_name == "TSBL Marketplace"
        assert settings.app_version == "1.0.0"
        assert settings.debug is False
        assert settings.environment == "development"

    def test_custom_values(self):
        settings = Settings(app_name="Test App", debug=True, environment="testing")
        assert settings.app_name == "Test App"
        assert settings.debug is True
        assert settings.environment == "testing"

    def test_database_url_default(self):
        settings = Settings()
        assert "postgresql+asyncpg://" in settings.database_url

    def test_redis_url_default(self):
        settings = Settings()
        assert "redis://" in settings.redis_url

    @patch("warnings.warn")
    def test_production_warnings(self, mock_warn):
        settings = Settings(
            environment="production",
            jwt_secret_key="change-this-in-production",
            encryption_key="change-this-in-production",
            debug=True,
        )
        settings.check_production_defaults()
        assert mock_warn.call_count >= 2

    @patch("warnings.warn")
    def test_no_warnings_in_dev(self, mock_warn):
        settings = Settings(environment="development")
        settings.check_production_defaults()
        mock_warn.assert_not_called()
