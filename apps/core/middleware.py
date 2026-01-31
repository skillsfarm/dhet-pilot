from django.shortcuts import render
from django.urls import reverse


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
