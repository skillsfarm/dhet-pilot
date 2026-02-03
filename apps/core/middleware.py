import logging
import time
import uuid

from django.conf import settings
from django.shortcuts import render
from django.urls import reverse

logger = logging.getLogger(__name__)


class RequestTracingMiddleware:
    """
    Middleware that adds request tracing with useful tags.

    Adds:
    - request_id: Unique identifier for each request
    - user: Username or email of authenticated user
    - mode: Application mode (development/testing/production)
    - Logs request/response details with timing
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.mode = getattr(settings, "MODE", "development")

    def __call__(self, request):
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        request.request_id = request_id

        # Get user info
        user = "anonymous"
        if hasattr(request, "user") and request.user.is_authenticated:
            user = (
                request.user.email
                if hasattr(request.user, "email") and request.user.email
                else str(request.user)
            )
        request.user_identifier = user

        # Start timing
        start_time = time.time()

        # Log incoming request
        extra = {
            "request_id": request_id,
            "user": user,
            "mode": self.mode,
        }

        # Only log detailed info in development mode
        if self.mode == "development":
            logger.info(
                f"[REQUEST] {request.method} {request.path}",
                extra=extra,
            )
            if request.GET:
                logger.debug(f"Query params: {dict(request.GET)}", extra=extra)

        # Process request
        response = self.get_response(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Add request_id to response headers
        response["X-Request-ID"] = request_id

        # Log response
        log_level = logging.INFO
        if response.status_code >= 500:
            log_level = logging.ERROR
        elif response.status_code >= 400:
            log_level = logging.WARNING

        logger.log(
            log_level,
            f"[RESPONSE] {request.method} {request.path} - {response.status_code} ({duration_ms:.2f}ms)",
            extra=extra,
        )

        # Log slow requests (> 1s) in production
        if duration_ms > 1000 and self.mode == "production":
            logger.warning(
                f"[SLOW REQUEST] {request.method} {request.path} took {duration_ms:.2f}ms",
                extra=extra,
            )

        return response

    def process_exception(self, request, exception):
        """Log exceptions with request context"""
        request_id = getattr(request, "request_id", "unknown")
        user = getattr(request, "user_identifier", "unknown")

        extra = {
            "request_id": request_id,
            "user": user,
            "mode": self.mode,
        }

        logger.error(
            f"[EXCEPTION] {request.method} {request.path} - {exception.__class__.__name__}: {str(exception)}",
            extra=extra,
            exc_info=True,
        )


class RestrictedAdminMiddleware:
    """
    Middleware that restricts access to the admin panel to staff users only.
    Authenticated non-staff users attempting to access /admin/ will be shown a 403 page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/"):
            # Allow login page through (which we overrode, but just in case)
            if request.path == "/admin/login/":
                return self.get_response(request)

            # If user is authenticated but not staff, show 403
            if request.user.is_authenticated and not request.user.is_staff:
                from apps.core.views_errors import access_denied

                return access_denied(request)

        response = self.get_response(request)
        return response
