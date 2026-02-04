import threading

from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse

from .forms import SignUpForm


class AccountAdapter(DefaultAccountAdapter):
    def get_signup_form_class(self, request):
        return SignUpForm

    def get_login_redirect_url(self, request):
        if request.user.is_superuser:
            return reverse("occupations")

        if request.user.is_staff:
            return reverse("occupations")

        return super().get_login_redirect_url(request)

    def send_mail(self, template_prefix, email, context):
        from allauth.core import context as allauth_context
        from django.contrib.sites.shortcuts import get_current_site

        request = allauth_context.request
        ctx = {
            "request": request,
            "email": email,
            "current_site": get_current_site(request),
        }
        ctx.update(context)
        msg = self.render_mail(template_prefix, email, ctx)

        def send_message():
            try:
                msg.send()
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send email to {email}: {str(e)}")

        # Send email in a separate thread to avoid blocking the response
        threading.Thread(target=send_message).start()
