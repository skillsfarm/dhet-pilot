from django.urls import path

from . import views

app_name = "candidates"

urlpatterns = [
    path("onboarding/", views.onboarding, name="onboarding"),
    path("onboarding/profile/", views.onboarding_profile, name="onboarding-profile"),
    path(
        "onboarding/education/", views.onboarding_education, name="onboarding-education"
    ),
    path(
        "onboarding/experience/",
        views.onboarding_experience,
        name="onboarding-experience",
    ),
    path("onboarding/targets/", views.onboarding_targets, name="onboarding-targets"),
    path(
        "onboarding/assessment/",
        views.onboarding_assessment,
        name="onboarding-assessment",
    ),
    path(
        "assessment/<str:occupation_id>/",
        views.occupation_assessment,
        name="occupation-assessment",
    ),
    path("assessments/", views.assessment_list, name="assessment-list"),
    path("feed/", views.content_feed, name="content-feed"),
    path("feed/<str:media_id>/", views.content_feed_detail, name="content-feed-detail"),
    path("admin/", views.candidate_list, name="candidate-list"),
    path("admin/add/", views.candidate_add, name="candidate-add"),
    path(
        "admin/<str:candidate_id>/edit/",
        views.candidate_edit_dashboard,
        name="candidate-edit",
    ),
    path(
        "admin/<str:candidate_id>/edit/profile/",
        views.candidate_edit_profile,
        name="candidate-edit-profile",
    ),
    path(
        "admin/<str:candidate_id>/edit/education/",
        views.candidate_edit_education,
        name="candidate-edit-education",
    ),
    path(
        "admin/<str:candidate_id>/edit/experience/",
        views.candidate_edit_experience,
        name="candidate-edit-experience",
    ),
    path(
        "admin/<str:candidate_id>/edit/targets/",
        views.candidate_edit_targets,
        name="candidate-edit-targets",
    ),
    path(
        "admin/<str:candidate_id>/edit/assessments/",
        views.candidate_edit_assessments,
        name="candidate-edit-assessments",
    ),
    path(
        "admin/<str:candidate_id>/edit/files/",
        views.candidate_edit_files,
        name="candidate-edit-files",
    ),
    path(
        "admin/<str:candidate_id>/edit/status/",
        views.candidate_mark_stats_recompute,
        name="candidate-edit-status",
    ),
    path(
        "admin/<str:candidate_id>/delete/",
        views.candidate_delete,
        name="candidate-delete",
    ),
]
