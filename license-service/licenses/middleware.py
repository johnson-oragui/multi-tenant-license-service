"""
Middleware
"""

# pylint: disable=broad-exception-caught, protected-access

import json
import logging
import time
import uuid
from typing import Any

from django.http import HttpRequest, HttpResponse, QueryDict
from django.utils.deprecation import MiddlewareMixin

MAX_BODY_SIZE = 10_000  # prevent huge payload logging

logger = logging.getLogger("request.audit")

SENSITIVE_KEYS = {
    "password",
    "pass",
    "secret",
    "api_key",
    "apikey",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "license_key",
}


def _safe_json(value: Any) -> Any:
    """
    safe json
    """
    try:
        json.dumps(value)
        return value
    except Exception:
        return str(value)


class RequestResponseLoggerMiddleware(MiddlewareMixin):
    """
    Logs request/response lifecycle details for audit and observability.
    """

    def process_request(self, request: HttpRequest) -> None:
        """
        Process requests
        """
        request._audit_start_time = time.monotonic()  # type: ignore
        request._correlation_id = request.headers.get(  # type: ignore
            "X-Correlation-ID", str(uuid.uuid4())
        )
        body = request.body[:MAX_BODY_SIZE].decode()
        content_type = request.META.get("CONTENT_TYPE", "")
        if "application/json" in content_type and body:
            request_body = self._obfuscate(json.loads(body))

        elif "multipart/form-data" in content_type:
            print("content_type: ", content_type)
            request_body = self._obfuscate(dict(request.POST))

        elif "application/x-www-form-urlencoded" in content_type:
            # Handle form-encoded data
            request_body = self._obfuscate(dict(QueryDict(body)))
        else:
            # Unknown content type, log raw body or skip
            request_body = body
        log_payload = {
            "correlation_id": request._correlation_id,  # type: ignore
            "method": request.method,
            "path": request.path,
            "brand_id": getattr(request.user, "id", "Guest"),
            "ip": self._get_ip(request),
            "user_agent": request.headers.get("User-Agent"),
            "payload": request_body,
        }

        logger.info("%s", json.dumps(log_payload, default=str))

    def process_response(
        self,
        request: HttpRequest,
        response: HttpResponse,
    ) -> HttpResponse:
        """
        process response
        """
        try:
            duration_ms = int(
                (time.monotonic() - getattr(request, "_audit_start_time", time.monotonic())) * 1000
            )

            response_body = None
            if hasattr(response, "data"):
                response_body = _safe_json(response.data)  # type: ignore

            log_payload = {
                "correlation_id": request._correlation_id,  # type: ignore
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "brand_id": getattr(request.user, "id", "Guest"),
                "response_body": self._obfuscate(response_body),
            }

            logger.info("%s", json.dumps(log_payload, default=str))
        except Exception:
            logger.exception("Request logging failed")

        response["X-Correlation-ID"] = request._correlation_id  # type: ignore
        return response

    @staticmethod
    def _get_ip(request: HttpRequest) -> str | None:
        """
        get ip
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

    def _obfuscate(
        self,
        value: Any,
        *,
        keep_last: int = 4,
    ) -> Any:
        """
        Recursively obfuscate sensitive values for console logs.
        """

        try:
            if isinstance(value, dict):
                return {
                    k: (
                        "***REDACTED***"
                        if k.lower() in SENSITIVE_KEYS
                        else self._obfuscate(v, keep_last=keep_last)
                    )
                    for k, v in value.items()
                }

            if isinstance(value, list):
                return [self._obfuscate(v, keep_last=keep_last) for v in value]

            if isinstance(value, str):
                if len(value) <= keep_last:
                    return "***REDACTED***"
                return f"***{value[-keep_last:]}"

            return value

        except Exception:
            return "***REDACTED***"
