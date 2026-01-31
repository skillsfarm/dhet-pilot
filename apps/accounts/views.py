from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.core.context_processors import navbar_context
from .forms import ProfileForm


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect(request.path)
    else:
        form = ProfileForm(instance=request.user)

    context = navbar_context(request)
    context["form"] = form
    return render(request, "accounts/profile.html", context)


@login_required
def profile_account(request):
    """HTMX partial view for account information tab"""
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
    else:
        form = ProfileForm(instance=request.user)

    context = navbar_context(request)
    context["form"] = form
    return render(request, "accounts/partials/profile_account.html", context)


@login_required
def profile_security(request):
    """HTMX partial view for security tab"""
    context = navbar_context(request)
    return render(request, "accounts/partials/profile_security.html", context)


@login_required
def profile_onboarding(request):
    """HTMX partial view for onboarding tab"""
    from rolepermissions.checkers import has_role

    # Prevent privileged users from accessing this view
    if (
        has_role(request.user, "content_manager")
        or has_role(request.user, "admin")
        or has_role(request.user, "super_admin")
    ):
        return redirect("dashboard")

    # Prevent already-onboarded users from viewing this
    if request.user.profile.is_onboarded:
        return redirect("dashboard")

    context = navbar_context(request)
    return render(request, "accounts/partials/profile_onboarding.html", context)


@login_required
def onboarding(request):
    """View to handle the onboarding process (Identity Step)"""
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            # Update onboarding status
            profile = user.profile
            if not profile.is_onboarded:
                # Basic identity update gives 10 points
                profile.onboarding_score = 10
                profile.is_onboarded = True
                profile.save()
                # Update session to reflect new status
                request.session["is_onboarded"] = True

            messages.success(request, "Identity information updated!")
            if profile.is_onboarded:
                return redirect("dashboard")
            return redirect("onboarding")
    else:
        form = ProfileForm(instance=request.user)

    context = navbar_context(request)
    context["form"] = form
    return render(request, "core/onboarding.html", context)
