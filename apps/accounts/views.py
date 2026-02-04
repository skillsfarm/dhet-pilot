from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
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
def profile_education(request):
    """HTMX partial view for education history tab"""
    from django.http import HttpResponseForbidden
    from apps.candidates.forms import EducationHistoryForm
    from apps.candidates.models import EducationHistory

    # Ensure user has a candidate profile
    if not hasattr(request.user, "candidate"):
        return HttpResponseForbidden("You do not have a candidate profile.")

    candidate = request.user.candidate

    if request.method == "POST":
        form = EducationHistoryForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.candidate = candidate
            education.save()
            messages.success(request, "Education history added successfully!")
            # Reset form for display
            form = EducationHistoryForm()
    else:
        form = EducationHistoryForm()

    education_history = EducationHistory.objects.filter(candidate=candidate)

    context = navbar_context(request)
    context.update(
        {
            "form": form,
            "education_history": education_history,
        }
    )
    return render(request, "accounts/partials/profile_education.html", context)


@login_required
def profile_education_detail(request, pk):
    """HTMX view for updating/deleting specific education items"""
    from django.shortcuts import get_object_or_404
    from django.http import HttpResponse, HttpResponseForbidden
    from apps.candidates.forms import EducationHistoryForm
    from apps.candidates.models import EducationHistory

    # Ensure user has a candidate profile
    if not hasattr(request.user, "candidate"):
        return HttpResponseForbidden("You do not have a candidate profile.")

    education = get_object_or_404(
        EducationHistory, pk=pk, candidate=request.user.candidate
    )

    if request.method == "DELETE":
        education.delete()
        return HttpResponse("")

    if request.method == "POST":
        form = EducationHistoryForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, "Education history updated!")
            # Render the item template with the updated form
            return render(
                request, "accounts/partials/item_education.html", {"edu": education}
            )

    # If GET or invalid form, render item
    # Note: For invalid form, we'd typically pass the form with errors.
    # But here we are just swapping the item.
    # To keep it simple for now, we'll re-render the item.
    return render(request, "accounts/partials/item_education.html", {"edu": education})


@login_required
def profile_experience(request):
    """HTMX partial view for work experience tab"""
    from django.http import HttpResponseForbidden
    from apps.candidates.forms import WorkExperienceForm
    from apps.candidates.models import WorkExperience

    # Ensure user has a candidate profile
    if not hasattr(request.user, "candidate"):
        return HttpResponseForbidden("You do not have a candidate profile.")

    candidate = request.user.candidate

    if request.method == "POST":
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.candidate = candidate
            experience.save()
            messages.success(request, "Work experience added successfully!")
            # Reset form for display
            form = WorkExperienceForm()
    else:
        form = WorkExperienceForm()

    work_experience = WorkExperience.objects.filter(candidate=candidate)

    context = navbar_context(request)
    context.update(
        {
            "form": form,
            "work_experience": work_experience,
        }
    )
    return render(request, "accounts/partials/profile_experience.html", context)


@login_required
def profile_experience_detail(request, pk):
    """HTMX view for updating/deleting specific work experience items"""
    from django.shortcuts import get_object_or_404
    from django.http import HttpResponse, HttpResponseForbidden
    from apps.candidates.forms import WorkExperienceForm
    from apps.candidates.models import WorkExperience

    # Ensure user has a candidate profile
    if not hasattr(request.user, "candidate"):
        return HttpResponseForbidden("You do not have a candidate profile.")

    experience = get_object_or_404(
        WorkExperience, pk=pk, candidate=request.user.candidate
    )

    if request.method == "DELETE":
        experience.delete()
        return HttpResponse("")

    if request.method == "POST":
        form = WorkExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, "Work experience updated!")
            return render(
                request, "accounts/partials/item_experience.html", {"job": experience}
            )

    return render(
        request, "accounts/partials/item_experience.html", {"job": experience}
    )


@login_required
def profile_targets(request):
    """HTMX partial view for target occupations tab"""
    from django.http import HttpResponseForbidden
    from apps.candidates.forms import OccupationTargetForm
    from apps.candidates.models import OccupationTarget

    # Ensure user has a candidate profile
    if not hasattr(request.user, "candidate"):
        return HttpResponseForbidden("You do not have a candidate profile.")

    candidate = request.user.candidate

    if request.method == "POST":
        form = OccupationTargetForm(request.POST, candidate=candidate)
        if form.is_valid():
            try:
                target = form.save(commit=False)
                target.candidate = candidate
                target.save()
                messages.success(request, "Target occupation added successfully!")
                # Reset form with fresh context
                form = OccupationTargetForm(candidate=candidate)
            except Exception as e:
                # Fallback for unique constraints if they slip through (though form validation handles most)
                messages.error(request, str(e))
    else:
        form = OccupationTargetForm(candidate=candidate)

    target_occupations = OccupationTarget.objects.filter(
        candidate=candidate
    ).select_related("occupation")

    context = navbar_context(request)
    context.update(
        {
            "form": form,
            "target_occupations": target_occupations,
        }
    )
    return render(request, "accounts/partials/profile_targets.html", context)


@login_required
def profile_targets_detail(request, pk):
    """HTMX view for updating/deleting specific target occupations"""
    from django.shortcuts import get_object_or_404
    from django.http import HttpResponseForbidden
    from apps.candidates.models import OccupationTarget

    # Ensure user has a candidate profile
    if not hasattr(request.user, "candidate"):
        return HttpResponseForbidden("You do not have a candidate profile.")

    target = get_object_or_404(
        OccupationTarget, pk=pk, candidate=request.user.candidate
    )

    if request.method == "DELETE":
        target.delete()
        messages.success(request, "Target occupation removed.")
        # Return the full list view to refresh the count and footer
        return profile_targets(request)

    # Calculate available priorities for the dropdown
    # Defined priorities map
    ALL_PRIORITIES = [
        (1, "High Priority"),
        (2, "Medium Priority"),
        (3, "Low Priority"),
    ]
    # Get priorities taken by OTHER targets
    taken_priorities = (
        OccupationTarget.objects.filter(candidate=request.user.candidate)
        .exclude(pk=pk)
        .values_list("priority", flat=True)
    )

    available_priorities = [p for p in ALL_PRIORITIES if p[0] not in taken_priorities]

    start_editing = request.GET.get("mode") == "edit"

    if request.method == "POST":
        # We only allow updating priority
        new_priority = request.POST.get("priority")

        if new_priority:
            new_priority = int(new_priority)
            if new_priority in taken_priorities:
                messages.error(request, f"Priority {new_priority} is already taken.")
                # Keep editing open if there was an error
                start_editing = True
            else:
                target.priority = new_priority
                target.save()
                messages.success(request, "Target priority updated!")
                # Close edit mode on success
                start_editing = False

        return render(
            request,
            "accounts/partials/item_target.html",
            {
                "target": target,
                "available_priorities": available_priorities,
                "start_editing": start_editing,
            },
        )

    return render(
        request,
        "accounts/partials/item_target.html",
        {
            "target": target,
            "available_priorities": available_priorities,
            "start_editing": start_editing,
        },
    )


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


@login_required
def user_list(request):
    """
    List all users. Accessible by superadmin, admin, and developer.
    """
    from django.core.paginator import Paginator
    from django.db.models import Q
    from rolepermissions.checkers import has_role

    if not (
        request.user.is_superuser
        or has_role(request.user, "admin")
        or has_role(request.user, "developer")
        or has_role(request.user, "super_admin")
    ):
        return redirect("dashboard")

    query = request.GET.get("q", "")
    users_qs = get_user_model().objects.all().order_by("-date_joined")

    if query:
        users_qs = users_qs.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

    paginator = Paginator(users_qs, 20)  # Show 20 users per page
    page_number = request.GET.get("page")
    users_page = paginator.get_page(page_number)

    context = navbar_context(request)
    context.update(
        {
            "users": users_page,
            "search_query": query,
        }
    )
    return render(request, "accounts/user_list.html", context)


@login_required
def user_edit(request, pk):
    """
    Edit a user. Accessible by superadmin, admin, and developer.
    """
    from django.shortcuts import get_object_or_404
    from rolepermissions.checkers import has_role
    from .forms import UserAdminForm

    if not (
        request.user.is_superuser
        or has_role(request.user, "admin")
        or has_role(request.user, "developer")
        or has_role(request.user, "super_admin")
    ):
        return redirect("dashboard")

    User = get_user_model()
    target_user = get_object_or_404(User, pk=pk)

    # Prevent non-superusers from editing superusers
    if target_user.is_superuser and not request.user.is_superuser:
        messages.error(request, "You do not have permission to edit a superuser.")
        return redirect("user_list")

    if request.method == "POST":
        form = UserAdminForm(request.POST, instance=target_user, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"User {target_user.username} updated successfully!"
            )
            return redirect("user_list")
    else:
        form = UserAdminForm(instance=target_user, user=request.user)

    context = navbar_context(request)
    context.update(
        {
            "form": form,
            "target_user": target_user,
        }
    )
    return render(request, "accounts/user_edit.html", context)
