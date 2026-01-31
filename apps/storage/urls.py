from django.urls import path
from .views import PresignedUploadView, ConfirmUploadView

urlpatterns = [
    path("presigned-url/", PresignedUploadView.as_view(), name="presigned-url"),
    path("confirm-upload/", ConfirmUploadView.as_view(), name="confirm-upload"),
]
