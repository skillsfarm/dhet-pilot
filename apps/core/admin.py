from django.contrib import admin
from django.contrib.admin.exceptions import NotRegistered
from dhet_admin.admin import ModelAdmin, TabularInline
from cookie_consent.models import CookieGroup, Cookie
from .models import UserCookieConsent

class CookieInline(TabularInline):
    model = Cookie
    extra = 1
    fields = ["name", "domain", "path", "description"]

class CookieGroupAdmin(ModelAdmin):
    list_display = ["name", "varname", "is_required", "is_deletable", "ordering"]
    list_filter = ["is_required", "is_deletable"]
    search_fields = ["name", "varname", "description"]
    inlines = [CookieInline]
    ordering = ["ordering"]

class CookieAdmin(ModelAdmin):
    list_display = ["name", "cookiegroup", "domain", "path"]
    list_filter = ["cookiegroup", "domain"]
    search_fields = ["name", "description", "domain"]
    raw_id_fields = ["cookiegroup"]

try:
    admin.site.unregister(CookieGroup)
except NotRegistered:
    pass

try:
    admin.site.unregister(Cookie)
except NotRegistered:
    pass

admin.site.register(CookieGroup, CookieGroupAdmin)
admin.site.register(Cookie, CookieAdmin)

@admin.register(UserCookieConsent)
class UserCookieConsentAdmin(ModelAdmin):
    list_display = ["user", "group_varname", "action", "version", "created_at"]
    list_filter = ["action", "group_varname", "created_at"]
    search_fields = ["user__username", "user__email", "group_varname"]
    readonly_fields = ["user", "group_varname", "action", "version", "created_at"]
