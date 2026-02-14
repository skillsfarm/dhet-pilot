from django.urls import path

from .views import file_list, file_detail, file_delete

urlpatterns = [
    path("files/", file_list, name="file-list"),
    path("files/<str:file_id>/", file_detail, name="file-detail"),
    path("files/<str:file_id>/delete/", file_delete, name="file-delete"),
]
