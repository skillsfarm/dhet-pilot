from rest_framework import serializers


class PresignedUploadSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=255, help_text="Desired filename")
    file_type = serializers.CharField(
        max_length=100, required=False, help_text="MIME type (e.g. image/png)"
    )
    folder = serializers.CharField(
        max_length=50,
        required=False,
        default="uploads",
        help_text="Target folder (default: uploads)",
    )


class PresignedUploadResponseSerializer(serializers.Serializer):
    upload_url = serializers.URLField(help_text="PUT this URL with the file content")
    file_url = serializers.URLField(
        help_text="Final public URL of the file after upload"
    )
    key = serializers.CharField(help_text="S3 key (path) of the file")


class ConfirmUploadSerializer(serializers.Serializer):
    key = serializers.CharField(
        help_text="The S3 key (path) provided in the presigned URL response"
    )
    original_name = serializers.CharField(
        required=False, help_text="Original filename for display"
    )
    mimetype = serializers.CharField(required=False, help_text="MIME specific type")
    size = serializers.IntegerField(required=False, help_text="File size in bytes")
