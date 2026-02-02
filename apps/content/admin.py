from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Industry, Occupation, OccupationTask, Skill


class OccupationTaskInline(admin.TabularInline):
    model = OccupationTask
    extra = 1
    fields = ["title", "description"]


@admin.register(Industry)
class IndustryAdmin(SimpleHistoryAdmin):
    list_display = ["name", "code"]
    search_fields = ["name", "code"]
    history_list_display = ["name", "code"]


@admin.register(Occupation)
class OccupationAdmin(SimpleHistoryAdmin):
    list_display = ["ofo_code", "ofo_title", "industry", "years_of_experience"]
    search_fields = ["ofo_code", "ofo_title", "industry__name"]
    list_filter = ["industry", "years_of_experience"]
    inlines = [OccupationTaskInline]
    history_list_display = ["ofo_code", "ofo_title"]


@admin.register(OccupationTask)
class OccupationTaskAdmin(SimpleHistoryAdmin):
    list_display = ["title", "occupation"]
    search_fields = ["title", "occupation__ofo_code", "occupation__ofo_title"]
    list_filter = ["occupation"]
    filter_horizontal = ["skills"]
    history_list_display = ["title"]


@admin.register(Skill)
class SkillAdmin(SimpleHistoryAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    history_list_display = ["name"]
