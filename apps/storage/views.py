import time
import os
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import views, status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import File
from .serializers import (
    PresignedUploadSerializer,
    PresignedUploadResponseSerializer,
    ConfirmUploadSerializer,
)
from .utils import generate_presigned_upload_url


class PresignedUploadView(views.APIView):
    """
    Generates a presigned URL for direct-to-storage (S3/Spaces) uploads.
    User PUTs the file to the returned `upload_url`.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=PresignedUploadSerializer,
        responses={200: PresignedUploadResponseSerializer},
        summary="Get S3/Spaces Presigned Upload URL",
        description="Returns a time-limited URL to upload a file directly to the object storage.",
    )
    def post(self, request):
        serializer = PresignedUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        filename = data["filename"]
        file_type = data.get("file_type")
        folder = data.get("folder", "uploads")

        # Sanitize and unique-ify filename
        root, ext = os.path.splitext(filename)
        clean_name = f"{root}_{int(time.time())}{ext}"
        key = f"{folder}/{clean_name}"

        # Generate URL
        upload_url = generate_presigned_upload_url(key, file_type=file_type)

        if not upload_url:
            return Response(
                {"error": "Could not generate upload URL. Check server configuration."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # construct hypothetical public URL (or use util if accessible)
        # Note: This checks settings to build the URL assuming public-read.
        # If private, client usually needs another call to get a download URL.
        bucket_name = settings.STORAGE_BUCKET_NAME
        endpoint = getattr(settings, "S3_ENDPOINT_URL", None)
        custom_domain = getattr(settings, "S3_CUSTOM_DOMAIN", None)

        if custom_domain:
            final_url = f"https://{custom_domain}/{key}"
        elif endpoint:
            final_url = f"{endpoint}/{bucket_name}/{key}"
        else:
            final_url = f"https://{bucket_name}.s3.amazonaws.com/{key}"

        return Response({"upload_url": upload_url, "file_url": final_url, "key": key})


class ConfirmUploadView(views.APIView):
    """
    Verifies that a file created via presigned URL actually exists in storage,
    and then creates a File record for it.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ConfirmUploadSerializer,
        summary="Confirm Upload Completion",
        description="Notify server that a client-side upload has finished. Server verifies existence and saves metadata.",
    )
    def post(self, request):
        serializer = ConfirmUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        key = data["key"]

        # 1. Verify existence in S3
        if not default_storage.exists(key):
            return Response(
                {
                    "error": "File not found in storage. Upload may have failed or key is incorrect."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2. Create File Record
        # We pass 'key' to the file field. Django's S3 storage handles this by pointing to that key.
        # We manually pass metadata if provided to skip re-fetching,
        # but our model's save() overrides might fetch if self.size is 0.

        file_obj = File(
            uploaded_by=request.user,
            file=key,  # The relative path in the bucket
            original_name=data.get("original_name", ""),
            mimetype=data.get("mimetype", ""),
            display_name=data.get("original_name", ""),
        )

        if data.get("size"):
            file_obj.size = data["size"]

        file_obj.save()

        return Response(
            {"id": file_obj.id, "status": "confirmed", "url": file_obj.file.url}
        )
