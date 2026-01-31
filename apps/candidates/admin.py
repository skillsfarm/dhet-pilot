from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    AssessmentResponse,
    CandidateProfile,
    EducationHistory,
    OccupationTarget,
    WorkExperience,
)


class EducationHistoryInline(admin.TabularInline):
    model = EducationHistory
    extra = 1
    fields = ["education_type", "institution", "field_of_study", "year_completed"]


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 1
    fields = ["job_title", "company", "start_date", "end_date"]


class OccupationTargetInline(admin.TabularInline):
    model = OccupationTarget
    extra = 1
    fields = ["occupation", "priority"]


class AssessmentResponseInline(admin.TabularInline):
    from .models import AssessmentResponse
    model = AssessmentResponse
    extra = 0
    readonly_fields = ["task", "response"]
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(CandidateProfile)
class CandidateProfileAdmin(SimpleHistoryAdmin):
    list_display = ["user", "get_education_count", "get_experience_count", "get_assessment_count"]
    search_fields = ["user__username", "user__email"]
    inlines = [EducationHistoryInline, WorkExperienceInline, OccupationTargetInline, AssessmentResponseInline]

    def get_education_count(self, obj):
        return obj.education_history.count()

    get_education_count.short_description = "Education Records"

    def get_experience_count(self, obj):
        return obj.work_experience.count()

    get_experience_count.short_description = "Work Experience"
    
    def get_assessment_count(self, obj):
        return obj.assessment_responses.count()
        
    get_assessment_count.short_description = "Assessment Responses"


@admin.register(EducationHistory)
class EducationHistoryAdmin(SimpleHistoryAdmin):
    list_display = ["candidate", "education_type", "institution", "year_completed"]
    search_fields = [
        "candidate__user__username",
        "institution",
        "field_of_study",
    ]
    list_filter = ["education_type", "year_completed"]
    history_list_display = ["education_type", "institution"]


@admin.register(WorkExperience)
class WorkExperienceAdmin(SimpleHistoryAdmin):
    list_display = ["candidate", "job_title", "company", "start_date", "end_date"]
    search_fields = ["candidate__user__username", "job_title", "company"]
    list_filter = ["start_date"]
    filter_horizontal = ["tasks", "skills"]
    history_list_display = ["job_title", "company"]


@admin.register(OccupationTarget)
class OccupationTargetAdmin(SimpleHistoryAdmin):
    list_display = ["candidate", "occupation", "priority"]
    search_fields = [
        "candidate__user__username",
        "occupation__ofo_code",
        "occupation__ofo_title",
    ]
    list_filter = ["priority"]
    history_list_display = ["occupation", "priority"]


@admin.register(AssessmentResponse)
class AssessmentResponseAdmin(SimpleHistoryAdmin):
    from .models import AssessmentResponse
    list_display = ["candidate", "task", "response"]
    search_fields = ["candidate__user__username", "task__title", "task__occupation__ofo_title"]
    list_filter = ["response"]
    history_list_display = ["task", "response"]
