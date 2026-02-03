from django.urls import path
from . import views

urlpatterns = [
    path("occupations/<str:occupation_id>/edit/", views.occupation_edit, name="occupation-edit"),
    
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
]
