from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from apps.storage.models import File
import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Tests file upload to the configured storage backend and cleans up."

    def handle(self, *args, **options):
        logger.info("Starting storage test...")

        # 1. Create content
        file_name = f"test_file_{int(time.time())}.txt"
        content = b"Hello, DigitalOcean Spaces! This is a test file."
        content_file = ContentFile(content)
        content_file.name = file_name  # Important for automatic name detection

        logger.info(f"Creating file: {file_name}")

        # 2. Save to model (triggers upload)
        # We don't need to manually set size/mime, the model should do it
        obj = File(display_name="Test Upload")
        obj.file = content_file
        obj.save()

        file_url = obj.file.url
        file_path = obj.file.name
        logger.info(f"File uploaded successfully! URL: {file_url}")

        # 3. Verify Metadata extraction
        logger.info("Metadata verified:")
        logger.info(f"- Size: {obj.size} bytes (Expected: {len(content)})")
        logger.info(f"- Mime: {obj.mimetype} (Expected: text/plain)")
        logger.info(f"- Ext: {obj.extension} (Expected: txt)")
        logger.info(f"- Original Name: {obj.original_name}")

        if obj.size == len(content) and obj.extension == "txt":
            logger.info("Metadata extraction worked correctly!")
        else:
            logger.error("Metadata extraction FAILED.")

        # 4. Verify file exists in storage
        if default_storage.exists(file_path):
            logger.info(f"Confirmed file exists in storage at: {file_path}")
        else:
            logger.error(f"File not found in storage at: {file_path}")
            # Cleanup DB object anyway
            obj.delete()
            return

        # 5. Cleanup
        logger.info("Cleaning up...")

        # Delete the object from DB
        obj.delete()
        logger.info("Database object deleted.")

        # Explicitly delete the file from storage (Django default behavior doesn't delete files on model delete)
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
            logger.info("File deleted from storage.")
        else:
            logger.warning("File was already gone from storage.")

        # Double check
        if not default_storage.exists(file_path):
            logger.info("Cleanup verification successful: File is gone.")
        else:
            logger.error("Cleanup failed: File still exists.")
