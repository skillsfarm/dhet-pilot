from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from dhet_admin.admin import ModelAdmin, TabularInline

from .models import Industry, Occupation, OccupationTask, Skill


class OccupationTaskInline(TabularInline):
    model = OccupationTask
    extra = 1
    fields = ["title", "description"]


@admin.register(Industry)
class IndustryAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ["name", "code"]
    search_fields = ["name", "code"]
    history_list_display = ["name", "code"]


@admin.register(Occupation)
class OccupationAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ["ofo_code", "ofo_title", "industry", "years_of_experience"]
    search_fields = ["ofo_code", "ofo_title", "industry__name"]
    list_filter = ["industry", "years_of_experience"]
    inlines = [OccupationTaskInline]
    history_list_display = ["ofo_code", "ofo_title"]
    raw_id_fields = ["industry"]


@admin.register(OccupationTask)
class OccupationTaskAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ["title", "occupation", "get_skill_count"]
    search_fields = ["title", "occupation__ofo_code", "occupation__ofo_title"]
    list_filter = ["occupation__industry", "occupation"]
    filter_horizontal = ["skills"]
    history_list_display = ["title"]
    raw_id_fields = ["occupation"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "occupation",
                    "title",
                    "description",
                )
            },
        ),
        (
            "Capabilities",
            {
                "fields": ("skills",),
                "description": "Select the skills required to perform this task.",
            },
        ),
    )

    @admin.display(description="Skills")
    def get_skill_count(self, obj):
        return obj.skills.count()


@admin.register(Skill)
class SkillAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    history_list_display = ["name"]
