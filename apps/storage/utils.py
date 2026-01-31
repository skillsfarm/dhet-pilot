import logging
import boto3
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)


def get_s3_client():
    from storages.backends.s3 import S3Storage

    storage = S3Storage()
    return storage.connection.meta.client


def generate_presigned_download_url(file_path, expiration=3600):
    """
    Generate a presigned URL to share a private file.
    """
    s3_client = get_s3_client()
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.STORAGE_BUCKET_NAME, "Key": file_path},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logger.error(e)
        return None
    return response


def generate_presigned_upload_url(object_name, expiration=3600, file_type=None):
    """
    Generate a presigned URL to upload a file directly to S3/Spaces from the client.
    """
    s3_client = get_s3_client()

    params = {
        "Bucket": settings.STORAGE_BUCKET_NAME,
        "Key": object_name,
    }

    if file_type:
        params["ContentType"] = file_type

    try:
        # Note: 'put_object' creates a URL for a PUT request
        response = s3_client.generate_presigned_url(
            "put_object", Params=params, ExpiresIn=expiration
        )
    except ClientError as e:
        logger.error(e)
        return None
    return response


def generate_presigned_post(object_name, expiration=3600):
    """
    Generate a presigned POST dictionary (for form uploads).
    Returns: {'url': '...', 'fields': {...}}
    """
    s3_client = get_s3_client()
    try:
        response = s3_client.generate_presigned_post(
            settings.STORAGE_BUCKET_NAME, object_name, ExpiresIn=expiration
        )
    except ClientError as e:
        logger.error(e)
        return None
    return response
