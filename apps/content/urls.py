from django.urls import path
from . import views

urlpatterns = [
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
