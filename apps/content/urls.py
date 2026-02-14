from django.urls import path
from . import views

urlpatterns = [
    path("industries/", views.industry_list, name="industry-list"),
    path("industries/add/", views.industry_add, name="industry-add"),
    path(
        "industries/<str:industry_id>/edit/",
        views.industry_edit,
        name="industry-edit",
    ),
    path(
        "industries/<str:industry_id>/delete/",
        views.industry_delete,
        name="industry-delete",
    ),
    path("skills/", views.skill_list, name="skill-list"),
    path("skills/add/", views.skill_add, name="skill-add"),
    path("skills/<str:skill_id>/edit/", views.skill_edit, name="skill-edit"),
    path(
        "skills/<str:skill_id>/delete/",
        views.skill_delete,
        name="skill-delete",
    ),
    path("occupations/add/", views.occupation_add, name="occupation-add"),
    path("occupations/upload/", views.occupation_upload, name="occupation-upload"),
    path(
        "occupations/<str:occupation_id>/edit/",
        views.occupation_edit,
        name="occupation-edit",
    ),
    path(
        "occupations/<str:occupation_id>/delete/",
        views.occupation_delete,
        name="occupation-delete",
    ),
    # HTMX Partials
    path(
        "occupations/<str:occupation_id>/partials/details/",
        views.occupation_details_partial,
        name="occupation-details-partial",
    ),
    path(
        "occupations/<str:occupation_id>/partials/tasks/",
        views.occupation_tasks_partial,
        name="occupation-tasks-partial",
    ),
    path(
        "occupations/<str:occupation_id>/partials/tasks/<str:task_id>/",
        views.occupation_task_detail,
        name="occupation-task-detail",
    ),
    path(
        "occupations/<str:occupation_id>/partials/media/",
        views.occupation_media_partial,
        name="occupation-media-partial",
    ),
    path(
        "occupations/<str:occupation_id>/partials/media/<str:media_id>/",
        views.occupation_media_detail,
        name="occupation-media-detail",
    ),
    path(
        "occupations/bulk-delete/",
        views.occupation_bulk_delete,
        name="occupation-bulk-delete",
    ),
    path(
        "occupations/partials/task-selector/",
        views.task_list_partial,
        name="task-list-partial",
    ),
]
