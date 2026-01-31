from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.contrib.admin.exceptions import NotRegistered
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group, Permission
from django.contrib.sites.admin import SiteAdmin as BaseSiteAdmin
from django.contrib.sites.models import Site
from allauth.account.admin import EmailAddressAdmin as BaseEmailAddressAdmin
from allauth.account.models import EmailAddress
from dhet_admin.admin import ModelAdmin, StackedInline

from .models import UserProfile

User = get_user_model()


class PermissionAdmin(ModelAdmin):
    """Custom PermissionAdmin with search fields for autocomplete."""

    search_fields = [
        "name",
        "codename",
        "content_type__app_label",
        "content_type__model",
    ]
    list_display = ["name", "content_type", "codename"]
    list_filter = ["content_type__app_label"]
    ordering = ["content_type__app_label", "codename"]


class UserProfileInline(StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fields = ("is_onboarded", "onboarding_score")


class UserAdmin(SimpleHistoryAdmin, BaseUserAdmin, ModelAdmin):
    inlines = [UserProfileInline]
    history_list_display = ["is_active"]
    autocomplete_fields = ["groups", "user_permissions"]

    # Use dhet_admin styled forms for proper password field styling
    from dhet_admin.forms import (
        UserCreationForm,
        UserChangeForm,
        AdminPasswordChangeForm,
    )

    add_form = UserCreationForm
    form = UserChangeForm
    change_password_form = AdminPasswordChangeForm

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "onboarding_progress",
    )

    def onboarding_progress(self, obj):
        try:
            score = obj.profile.onboarding_score
            percentage = score * 10
            color = "#ef4444"  # text-red-500
            if percentage >= 100:
                color = "#22c55e"  # text-green-500
            elif percentage >= 50:
                color = "#f59e0b"  # text-amber-500

            from django.utils.html import format_html

            return format_html(
                '<span style="color: {}; font-weight: bold;">{}%</span>',
                color,
                percentage,
            )
        except Exception:
            return "-"

    onboarding_progress.short_description = "Onboarding"


class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    """Custom GroupAdmin with dhet_admin styling."""

    search_fields = ["name"]
    autocomplete_fields = ["permissions"]


class SiteAdmin(BaseSiteAdmin, ModelAdmin):
    """Custom SiteAdmin with dhet_admin styling."""

    pass


class EmailAddressAdmin(BaseEmailAddressAdmin, ModelAdmin):
    """Custom EmailAddressAdmin with dhet_admin styling."""

    pass


# Unregister default admins and register custom ones
try:
    admin.site.unregister(User)
except NotRegistered:
    pass
admin.site.register(User, UserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

admin.site.unregister(Site)
admin.site.register(Site, SiteAdmin)

admin.site.unregister(EmailAddress)
admin.site.register(EmailAddress, EmailAddressAdmin)

admin.site.register(Permission, PermissionAdmin)
