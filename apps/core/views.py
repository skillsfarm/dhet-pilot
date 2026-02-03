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
from apps.content.models import Occupation, Industry


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


@login_required
def occupation_list(request):
    """
    List occupations with search and filtering.
    """
    # Base queryset
    occupations = Occupation.objects.select_related("industry").all()
    
    # Identify interested industries for candidates based on their targets
    interested_industry_ids = []
    if hasattr(request.user, "candidate"):
        from apps.candidates.models import OccupationTarget
        interested_industry_ids = OccupationTarget.objects.filter(
            candidate=request.user.candidate
        ).values_list("occupation__industry_id", flat=True).distinct()
        # Convert CUIDs to strings for template comparison if necessary, 
        # but here we use them for filtering.
    
    # Search
    query = request.GET.get("q")
    if query:
        occupations = occupations.filter(
            Q(ofo_title__icontains=query) | 
            Q(ofo_code__icontains=query) |
            Q(description__icontains=query)
        )
        
    # Filter by Industry
    industry_id = request.GET.get("industry")
    
    # If no industry selected and user is a candidate (not elevated), default to 'interested'
    from rolepermissions.checkers import has_role
    is_elevated = has_role(request.user, ["content_manager", "admin", "super_admin"])
    
    if not industry_id and not is_elevated and hasattr(request.user, "candidate") and len(interested_industry_ids) > 0:
        industry_id = "interested"
    
    if industry_id == "interested":
        if interested_industry_ids:
            occupations = occupations.filter(industry_id__in=interested_industry_ids)
    elif industry_id:
        occupations = occupations.filter(industry_id=industry_id)

    # Pagination
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(occupations, 10)  # Show 10 occupations per page
    page_number = request.GET.get('page')
    try:
        occupations = paginator.page(page_number)
    except PageNotAnInteger:
        occupations = paginator.page(1)
    except EmptyPage:
        occupations = paginator.page(paginator.num_pages)

    # If candidate, attach cached scores from recommended_occupations
    if hasattr(request.user, "candidate"):
        candidate = request.user.candidate
        # Build a lookup dict from cached proficiency data
        cached_scores = {}
        for item in candidate.recommended_occupations:
            cached_scores[item.get("ofo_code")] = item.get("score", 0)
        
        for occ in occupations:
            occ.proficiency_score = cached_scores.get(occ.ofo_code, 0)

    industries = Industry.objects.all()

    context = navbar_context(request)
    context.update({
        "occupations": occupations,
        "industries": industries,
        "search_query": query,
        "selected_industry": industry_id,
        "has_interests": len(interested_industry_ids) > 0,
    })
    
    return render(request, "core/occupation_list.html", context)


@login_required
def occupation_detail(request, occupation_id):
    """
    Detailed view of an occupation. 
    Shows description, tasks, and for candidates, action items.
    """
    from django.shortcuts import get_object_or_404
    
    # We use select_related to get industry data efficiently
    occupation = get_object_or_404(Occupation.objects.select_related("industry"), pk=occupation_id)
    
    context = navbar_context(request)
    context.update({
        "occupation": occupation,
    })
    
    # Candidate specific logic: Check if it's a target, get score, etc.
    if hasattr(request.user, "candidate"):
        candidate = request.user.candidate
        from apps.candidates.models import OccupationTarget
        context["is_target"] = OccupationTarget.objects.filter(candidate=candidate, occupation=occupation).exists()
        
        # Get score if available
        if candidate.recommended_occupations:
            for item in candidate.recommended_occupations:
                 if item.get("ofo_code") == occupation.ofo_code:
                     context["proficiency_score"] = item.get("score")
                     break
        
        # Check active assessment status
        if candidate.assessment_progress:
            progress_data = candidate.assessment_progress.get(occupation.ofo_code)
            if progress_data:
                context["assessment_progress_data"] = progress_data

    return render(request, "core/occupation_detail.html", context)

