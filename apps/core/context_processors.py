from django.urls import reverse
from rolepermissions.checkers import has_role


def resolve_role(user):
    if has_role(user, "super_admin"):
        return "super"
    if has_role(user, "admin"):
        return "admin"
    if has_role(user, "content_manager"):
        return "content-manager"
    if has_role(user, "developer"):
        return "developer"
    return "user"


def navbar_context(request):
    user = request.user
    role = resolve_role(user)
    show_api_docs = has_role(user, ["developer", "admin", "super_admin"])
    show_admin = has_role(user, ["admin", "super_admin"])

    # Check session for onboarding status, fallback to DB if missing
    is_onboarded = request.session.get("is_onboarded")
    if is_onboarded is None and hasattr(user, "profile"):
        is_onboarded = user.profile.is_onboarded
        request.session["is_onboarded"] = is_onboarded

    # Only show onboarding UI for standard 'user' role who haven't completed onboarding
    # Exclude users with elevated roles (developer, content_manager, admin, super_admin)
    is_elevated = has_role(
        user, ["developer", "content_manager", "admin", "super_admin"]
    )
    # If is_onboarded is None (e.g. no profile), assume True (don't show onboarding)
    # unless we want to force it? Defaulting to False (not onboarded) might be safer if profile is missing?
    # But usually profile exists. Stick to explicit False check.

    show_onboarding = False
    if has_role(user, "user") and not is_elevated:
        # If is_onboarded is False (explicitly), then show onboarding.
        # If is_onboarded is None (maybe weird state), we can check DB again or assume False?
        # Let's rely on the session/DB value.
        if is_onboarded is False:
            show_onboarding = True

    profile_url_name = f"{role}-profile"
    return {
        "role": role,
        "profile_url": reverse(profile_url_name),
        "show_api_docs": show_api_docs,
        "show_admin": show_admin,
        "show_onboarding": show_onboarding,
    }
