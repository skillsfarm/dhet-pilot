import logging
from django.core.mail import send_mail
from django.utils import timezone
from .models import Notification, NotificationLog

logger = logging.getLogger(__name__)


def create_and_send_notification(user, subject, message):
    """
    Creates a Notification and attempts to send it via email.
    """
    notification = Notification.objects.create(
        user=user, subject=subject, message=message, status="pending"
    )

    try:
        # Assuming user has an email attribute
        if not user.email:
            raise ValueError("User has no email address.")

        NotificationLog.objects.create(
            notification=notification, status="sending_attempt", details="Attempting to send email."
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings
            recipient_list=[user.email],
            fail_silently=False,
        )

        notification.status = "sent"
        notification.sent_at = timezone.now()
        notification.save()
        
        NotificationLog.objects.create(
            notification=notification, status="sent", details=f"Successfully sent to {user.email}"
        )
        logger.info(f"Notification sent to {user.email}: {notification.id}")
        return True, notification

    except Exception as e:
        logger.error(f"Failed to send notification to {user}: {e}")
        notification.status = "failed"
        notification.error_message = str(e)
        notification.save()
        
        NotificationLog.objects.create(
            notification=notification, status="failure", details=str(e)
        )
        return False, notification
