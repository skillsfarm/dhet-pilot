from django.db import models
import os
import mimetypes
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile as DjangoUploadedFile
from apps.core.models import CuidModel
from simple_history.models import HistoricalRecords


class File(CuidModel):
    """
    A specific file stored in the object storage (S3/Spaces).
    Stores metadata to avoid API calls to the storage provider.
    """

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_files",
    )

    # The file itself (path in bucket)
    file = models.FileField(upload_to="uploads/%Y/%m/%d/")

    # Metadata
    display_name = models.CharField(max_length=255, help_text="Human readable name")
    original_name = models.CharField(
        max_length=255, blank=True, help_text="Original filename on upload"
    )
    extension = models.CharField(max_length=50, blank=True)
    mimetype = models.CharField(max_length=100, blank=True)
    size = models.PositiveBigIntegerField(default=0, help_text="Size in bytes")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "File"
        verbose_name_plural = "Files"

    def __str__(self):
        return self.display_name or self.original_name

    def save(self, *args, **kwargs):
        # Check if this is a new file being uploaded
        if self.file and not self.size:
            # 1. Get size
            try:
                self.size = self.file.size
            except Exception:
                pass

            # 2. Extract filename info
            if not self.original_name:
                self.original_name = os.path.basename(self.file.name)

            if not self.display_name:
                self.display_name = self.original_name

            # 3. Extract Extension and Mime Type
            base, ext = os.path.splitext(self.original_name)
            self.extension = ext.lower().replace(".", "")

            if not self.mimetype:
                mime_type, _ = mimetypes.guess_type(self.original_name)
                self.mimetype = mime_type or "application/octet-stream"

        super().save(*args, **kwargs)

    @property
    def is_image(self):
        return self.mimetype.startswith("image/") if self.mimetype else False
