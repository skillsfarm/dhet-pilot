from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.context_processors import navbar_context
from apps.core.permissions import is_admin_or_super_admin
from apps.notifications.models import Notification, NotificationLog
from apps.notifications.services import create_and_send_notification
from django.contrib.auth import get_user_model
from rolepermissions.checkers import has_role


@login_required
@user_passes_test(is_admin_or_super_admin)
def notification_list(request):
    query = request.GET.get("q", "")
    notifications = Notification.objects.select_related("user").all()

    if query:
        notifications = notifications.filter(subject__icontains=query)

    context = navbar_context(request)
    context.update({"notifications": notifications, "search_query": query})
    return render(request, "notifications/notification_list.html", context)


@login_required
def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)
    is_admin = is_admin_or_super_admin(request.user)
    if not is_admin and notification.user != request.user:
        return redirect("notification-my-list")

    logs = NotificationLog.objects.filter(notification=notification)
    context = navbar_context(request)
    context.update({"notification": notification, "logs": logs, "is_admin": is_admin})
    return render(request, "notifications/notification_detail.html", context)


@login_required
@user_passes_test(is_admin_or_super_admin)
def notification_delete(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)
    if request.method == "POST" or request.method == "DELETE":
        notification.delete()
        messages.success(request, "Notification deleted successfully.")
        return redirect("notification-list")

    context = navbar_context(request)
    context["notification"] = notification
    return render(request, "notifications/notification_confirm_delete.html", context)


@login_required
@user_passes_test(is_admin_or_super_admin)
def notification_create(request):
    """
    Create and send notifications to selected user groups.
    """
    User = get_user_model()

    roles = ["user", "developer", "content_manager", "admin", "super_admin"]
    if request.method == "POST":
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()
        selected_roles = request.POST.getlist("roles")

        if not subject or not message:
            messages.error(request, "Subject and message are required.")
        elif not selected_roles:
            messages.error(request, "Select at least one role group.")
        else:
            recipients = []
            for user in User.objects.filter(is_active=True).exclude(email=""):
                if any(has_role(user, role) for role in selected_roles):
                    recipients.append(user)

            if not recipients:
                messages.error(request, "No recipients found for the selected roles.")
            else:
                sent_count = 0
                for user in recipients:
                    success, _ = create_and_send_notification(user, subject, message)
                    if success:
                        sent_count += 1
                messages.success(
                    request,
                    f"Sent notifications to {sent_count} user(s) out of {len(recipients)}.",
                )
                return redirect("notification-list")

    context = navbar_context(request)
    context.update({"roles": roles})
    return render(request, "notifications/notification_create.html", context)


@login_required
def notification_my_list(request):
    """Candidate notification inbox."""
    query = request.GET.get("q", "")
    notifications = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )

    if query:
        notifications = notifications.filter(subject__icontains=query)

    context = navbar_context(request)
    context.update({"notifications": notifications, "search_query": query})
    return render(request, "notifications/notification_my_list.html", context)
