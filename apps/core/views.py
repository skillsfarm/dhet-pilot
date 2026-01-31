from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from rolepermissions.checkers import has_role
import json

from cookie_consent.util import get_cookie_dict_from_request, get_cookie_groups, set_cookie_dict_to_response, delete_cookies
from .models import UserCookieConsent
from cookie_consent.conf import settings

from .context_processors import navbar_context


@login_required
def dashboard_redirect(request):
    """
    Central dispatch view to route users to their appropriate dashboard based on role.
    """
    if request.user.is_superuser:
        return redirect("super-profile")
    if request.user.is_staff:
        return redirect("admin-profile")
    if has_role(request.user, "content_manager"):
        return redirect("content-manager-dashboard")
        
    # Standard users go to the user dashboard
    return redirect("user-dashboard")


def home(request):
    """Redirect to dashboard dispatcher if logged in, otherwise to login page"""
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("account_login")


@login_required
def user_dashboard(request):
    context = navbar_context(request)
    
    # Extra check: Ensure standard users are TRULY onboarded (score >= 10)
    if not request.user.is_superuser and not request.user.is_staff and hasattr(request.user, "profile"):
        profile = request.user.profile
        if profile.is_onboarded and profile.onboarding_score < 10:
            # Fix inconsistent state
            profile.is_onboarded = False
            profile.save()
            request.session["is_onboarded"] = False
            return redirect("candidates:onboarding")

    if context.get("show_onboarding"):
        return redirect("candidates:onboarding")

    # Check for candidate stats updates
    if hasattr(request.user, "candidate"):
        candidate = request.user.candidate
        if candidate.stats_update_needed:
            from apps.candidates.services import compute_candidate_stats
            compute_candidate_stats(candidate)

    return render(request, "core/dashboard.html", context)


@login_required
def content_manager_dashboard(request):
    """
    Dashboard specifically for content managers.
    """
    if not has_role(request.user, "content_manager") and not request.user.is_superuser:
        return redirect("dashboard")
        
    context = navbar_context(request)
    return render(request, "core/dashboard.html", context)


@ensure_csrf_cookie
def save_cookie_preferences(request):
    """
    Saves all cookie preferences (accepted and declined) in a single request.
    This avoids race conditions and multiple round-trips.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            accepted_varnames = data.get("accepted", [])
            declined_varnames = data.get("declined", [])

            response = JsonResponse({"status": "ok"})
            cookie_dic = get_cookie_dict_from_request(request)

            if accepted_varnames:
                for group in get_cookie_groups(",".join(accepted_varnames)):
                    cookie_dic[group.varname] = group.get_version()
                    if request.user.is_authenticated:
                        UserCookieConsent.objects.create(
                            user=request.user,
                            group_varname=group.varname,
                            action="accepted",
                            version=str(group.get_version()),
                        )

            if declined_varnames:
                for group in get_cookie_groups(",".join(declined_varnames)):
                    cookie_dic[group.varname] = settings.COOKIE_CONSENT_DECLINE
                    delete_cookies(response, group)
                    if request.user.is_authenticated:
                        UserCookieConsent.objects.create(
                            user=request.user,
                            group_varname=group.varname,
                            action="declined",
                            version=str(group.get_version()),
                        )

            set_cookie_dict_to_response(response, cookie_dic)
            return response
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return HttpResponse(status=405)
