from django.contrib import admin
from dhet_admin.admin import ModelAdmin
from .models import UserCookieConsent

@admin.register(UserCookieConsent)
class UserCookieConsentAdmin(ModelAdmin):
    list_display = ["user", "group_varname", "action", "version", "created_at"]
    list_filter = ["action", "group_varname", "created_at"]
    search_fields = ["user__username", "user__email", "group_varname"]
    readonly_fields = ["user", "group_varname", "action", "version", "created_at"]
