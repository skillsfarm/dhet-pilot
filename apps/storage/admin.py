from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from apps.storage.models import File


@admin.register(File)
class FileAdmin(SimpleHistoryAdmin):
    list_display = [
        "display_name",
        "extension",
        "mimetype",
        "size",
        "uploaded_by",
        "created_at",
    ]
    list_filter = ["mimetype", "extension", "created_at"]
    search_fields = ["display_name", "original_name"]
    readonly_fields = [
        "original_name",
        "extension",
        "mimetype",
        "size",
        "created_at",
        "updated_at",
    ]
