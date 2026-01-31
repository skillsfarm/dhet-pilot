from allauth.account.adapter import DefaultAccountAdapter
from .forms import SignUpForm


class AccountAdapter(DefaultAccountAdapter):
    def get_signup_form_class(self, request):
        return SignUpForm

    def get_login_redirect_url(self, request):
        from django.urls import reverse

        if request.user.is_superuser:
            return reverse("super-profile")

        if request.user.is_staff:
            return reverse("admin-profile")

        return super().get_login_redirect_url(request)
