from django.conf import settings
from django.db import models
from apps.core.models import CuidModel
from simple_history.models import HistoricalRecords


class Notification(CuidModel):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    
    # We keep the latest error/sent status here for easy querying
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.user} - {self.subject} ({self.status})"

    class Meta:
        ordering = ["-created_at"]


class NotificationLog(CuidModel):
    """
    Log model to trace the lifecycle and delivery attempts of a notification.
    """
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="logs",
    )
    status = models.CharField(max_length=50)
    details = models.TextField(blank=True, null=True, help_text="SMTP response or error details")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.notification} - {self.status}"

    class Meta:
        ordering = ["-created_at"]
