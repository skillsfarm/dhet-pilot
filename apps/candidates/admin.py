from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.utils.html import format_html
from dhet_admin.admin import ModelAdmin, TabularInline

from .models import (
    AssessmentResponse,
    CandidateProfile,
    EducationHistory,
    OccupationTarget,
    WorkExperience,
)


class EducationHistoryInline(TabularInline):
    model = EducationHistory
    extra = 1
    fields = ["education_type", "institution", "field_of_study", "year_completed"]


class WorkExperienceInline(TabularInline):
    model = WorkExperience
    extra = 1
    fields = ["job_title", "company", "start_date", "end_date"]


class OccupationTargetInline(TabularInline):
    model = OccupationTarget
    extra = 1
    fields = ["occupation", "priority"]


class AssessmentResponseInline(TabularInline):
    from .models import AssessmentResponse
    model = AssessmentResponse
    extra = 0
    readonly_fields = ["task", "response"]
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(CandidateProfile)
class CandidateProfileAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ["user", "get_education_count", "get_experience_count", "get_assessment_count", "stats_update_needed", "stats_last_computed"]
    search_fields = ["user__username", "user__email"]
    list_filter = ["stats_update_needed"]
    readonly_fields = ["highest_nqf_level", "occupation_matches_count", "recommended_occupations", "assessment_progress", "stats_last_computed"]
    inlines = [EducationHistoryInline, WorkExperienceInline, OccupationTargetInline, AssessmentResponseInline]
    actions = ["recompute_stats", "mark_for_recompute"]
    
    fieldsets = (
        (None, {
            "fields": ("user",)
        }),
        ("Cached Stats", {
            "fields": ("highest_nqf_level", "occupation_matches_count", "assessment_progress", "recommended_occupations"),
            "classes": ("collapse",),
        }),
        ("Stats Management", {
            "fields": ("stats_update_needed", "stats_last_computed"),
        }),
    )

    def get_education_count(self, obj):
        return obj.education_history.count()

    get_education_count.short_description = "Education Records"

    def get_experience_count(self, obj):
        return obj.work_experience.count()

    get_experience_count.short_description = "Work Experience"
    
    def get_assessment_count(self, obj):
        return obj.assessment_responses.count()
        
    get_assessment_count.short_description = "Assessment Responses"
    
    @admin.action(description="Recompute stats now for selected candidates")
    def recompute_stats(self, request, queryset):
        from .services import compute_candidate_stats
        count = 0
        for candidate in queryset:
            compute_candidate_stats(candidate)
            count += 1
        self.message_user(request, f"Successfully recomputed stats for {count} candidate(s).")
    
    @admin.action(description="Mark selected candidates for stats update")
    def mark_for_recompute(self, request, queryset):
        count = queryset.update(stats_update_needed=True)
        self.message_user(request, f"Marked {count} candidate(s) for stats update.")


@admin.register(EducationHistory)
class EducationHistoryAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ["candidate", "education_type", "institution", "year_completed"]
    search_fields = [
        "candidate__user__username",
        "institution",
        "field_of_study",
    ]
    list_filter = ["education_type", "year_completed"]
    history_list_display = ["education_type", "institution"]


@admin.register(WorkExperience)
class WorkExperienceAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ["candidate", "job_title", "company", "start_date", "end_date"]
    search_fields = ["candidate__user__username", "job_title", "company"]
    list_filter = ["start_date"]
    filter_horizontal = ["tasks", "skills"]
    history_list_display = ["job_title", "company"]


@admin.register(OccupationTarget)
class OccupationTargetAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ["candidate", "occupation", "priority"]
    search_fields = [
        "candidate__user__username",
        "occupation__ofo_code",
        "occupation__ofo_title",
    ]
    list_filter = ["priority"]
    history_list_display = ["occupation", "priority"]


@admin.register(AssessmentResponse)
class AssessmentResponseAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ["candidate", "task_title", "occupation", "response"]
    search_fields = [
        "candidate__user__username",
        "candidate__user__email",
        "task__title",
        "task__occupation__ofo_title",
    ]
    list_filter = ["response", "task__occupation"]
    history_list_display = ["task", "response"]
    raw_id_fields = ["candidate", "task"]
    radio_fields = {"response": admin.HORIZONTAL}

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "candidate",
                    "task",
                )
            },
        ),
        (
            "Evaluation",
            {
                "fields": (
                    "get_task_description",
                    "response",
                ),
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly = ["get_task_description"]
        if obj:  # editing an existing object
            readonly += ["candidate", "task"]
        return readonly

    @admin.display(description="Task")
    def task_title(self, obj):
        return obj.task.title

    @admin.display(description="Occupation")
    def occupation(self, obj):
        return obj.task.occupation.ofo_title

    @admin.display(description="Task Description")
    def get_task_description(self, obj):
        if obj and obj.task:
            return format_html(
                '<div style="max-width: 600px; padding: 10px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 4px;">{}</div>',
                obj.task.description,
            )
        return "-"
