from __future__ import annotations

import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, header_name: str = "X-Correlation-ID") -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        correlation_id = request.headers.get(self.header_name)
        if not correlation_id:
            correlation_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        request.state.correlation_id = correlation_id

        response = await call_next(request)

        response.headers[self.header_name] = correlation_id
        return response
