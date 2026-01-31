from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from apps.storage.models import File
import time


class Command(BaseCommand):
    help = "Tests file upload to the configured storage backend and cleans up."

    def handle(self, *args, **options):
        self.stdout.write("Starting storage test...")

        # 1. Create content
        file_name = f"test_file_{int(time.time())}.txt"
        content = b"Hello, DigitalOcean Spaces! This is a test file."
        content_file = ContentFile(content)
        content_file.name = file_name  # Important for automatic name detection

        self.stdout.write(f"Creating file: {file_name}")

        # 2. Save to model (triggers upload)
        # We don't need to manually set size/mime, the model should do it
        obj = File(display_name="Test Upload")
        obj.file = content_file
        obj.save()

        file_url = obj.file.url
        file_path = obj.file.name
        self.stdout.write(
            self.style.SUCCESS(f"File uploaded successfully! URL: {file_url}")
        )

        # 3. Verify Metadata extraction
        self.stdout.write(f"Metadata verified:")
        self.stdout.write(f"- Size: {obj.size} bytes (Expected: {len(content)})")
        self.stdout.write(f"- Mime: {obj.mimetype} (Expected: text/plain)")
        self.stdout.write(f"- Ext: {obj.extension} (Expected: txt)")
        self.stdout.write(f"- Original Name: {obj.original_name}")

        if obj.size == len(content) and obj.extension == "txt":
            self.stdout.write(
                self.style.SUCCESS("Metadata extraction worked correctly!")
            )
        else:
            self.stdout.write(self.style.ERROR("Metadata extraction FAILED."))

        # 4. Verify file exists in storage
        if default_storage.exists(file_path):
            self.stdout.write(
                self.style.SUCCESS(f"Confirmed file exists in storage at: {file_path}")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"File not found in storage at: {file_path}")
            )
            # Cleanup DB object anyway
            obj.delete()
            return

        # 5. Cleanup
        self.stdout.write("Cleaning up...")

        # Delete the object from DB
        obj.delete()
        self.stdout.write("Database object deleted.")

        # Explicitly delete the file from storage (Django default behavior doesn't delete files on model delete)
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
            self.stdout.write(self.style.SUCCESS("File deleted from storage."))
        else:
            self.stdout.write(self.style.WARNING("File was already gone from storage."))

        # Double check
        if not default_storage.exists(file_path):
            self.stdout.write(
                self.style.SUCCESS("Cleanup verification successful: File is gone.")
            )
        else:
            self.stdout.write(self.style.ERROR("Cleanup failed: File still exists."))
