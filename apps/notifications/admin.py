from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Notification, NotificationLog


class NotificationLogInline(admin.TabularInline):
    model = NotificationLog
    readonly_fields = ('created_at', 'status', 'details')
    extra = 0
    can_delete = False


@admin.register(Notification)
class NotificationAdmin(SimpleHistoryAdmin):
    list_display = ('user', 'subject', 'status', 'created_at', 'sent_at')
    history_list_display = ["status"]
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'subject')
    readonly_fields = ('created_at', 'sent_at', 'status', 'error_message')
    inlines = [NotificationLogInline]
