from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

SUPPORTED_LOCALES = {"en", "bn", "ar", "hi", "ur", "es", "fr"}
DEFAULT_LOCALE = "en"


class LocalizationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, header_name: str = "Accept-Language") -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        raw_locale = request.headers.get(self.header_name, DEFAULT_LOCALE)
        locale = raw_locale.split(",")[0].split(";")[0].strip()[:2]

        if locale not in SUPPORTED_LOCALES:
            locale = DEFAULT_LOCALE

        request.state.locale = locale

        response = await call_next(request)

        response.headers["Content-Language"] = locale
        return response
