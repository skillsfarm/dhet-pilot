from django.contrib import messages
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.accounts.models import UserProfile
from apps.core.context_processors import navbar_context
from apps.core.permissions import is_admin_or_super_admin

from .forms import (
    CandidateCreateForm,
    CandidateUpdateForm,
    EducationHistoryForm,
    OccupationTargetForm,
    ProfileForm,
    WorkExperienceForm,
)
from .models import CandidateProfile, EducationHistory, OccupationTarget, WorkExperience
from apps.content.models import OccupationMedia


def get_or_create_candidate_profile(user):
    """Get or create candidate profile for user."""
    profile, _ = CandidateProfile.objects.get_or_create(user=user)
    return profile


def update_onboarding_score(user, new_score):
    """Update user's onboarding score."""
    user_profile, _ = UserProfile.objects.get_or_create(user=user)
    if new_score > user_profile.onboarding_score:
        user_profile.onboarding_score = new_score
        if new_score >= 10:
            user_profile.is_onboarded = True
        user_profile.save()
    return user_profile


@login_required
def onboarding(request):
    """Main onboarding page with tabbed navigation."""
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Redirect to dashboard if already onboarded (ensure score is actually complete)
    if user_profile.is_onboarded and user_profile.onboarding_score >= 10:
        return redirect("user-dashboard")

    # Self-healing: If score is less than 10, ensure is_onboarded is False
    if user_profile.onboarding_score < 10 and user_profile.is_onboarded:
        user_profile.is_onboarded = False
        user_profile.save()

    # Determine active tab based on score
    score = user_profile.onboarding_score
    if score < 2:
        active_tab = "profile"
    elif score < 4:
        active_tab = "education"
    elif score < 6:
        active_tab = "experience"
    elif score < 8:
        active_tab = "targets"
    else:
        active_tab = "assessment"

    context = navbar_context(request)
    context.update(
        {
            "onboarding_score": score,
            "active_tab": active_tab,
        }
    )

    return render(request, "candidates/onboarding.html", context)


@login_required
def onboarding_profile(request):
    """Profile step (Score 0→2)."""
    if request.method == "POST":
        form = ProfileForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            # Create candidate profile
            get_or_create_candidate_profile(request.user)
            # Update score
            user_profile = update_onboarding_score(request.user, 2)

            # Return updated partial or redirect to next step
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "candidates/partials/onboarding_education.html",
                    {
                        "form": EducationHistoryForm(),
                        "score": user_profile.onboarding_score,
                        "active_tab": "education",
                    },
                )
            return redirect("candidates:onboarding")
    else:
        form = ProfileForm(
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
            }
        )

    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(
        request,
        "candidates/partials/onboarding_profile.html",
        {"form": form, "score": user_profile.onboarding_score, "active_tab": "profile"},
    )


@login_required
def onboarding_education(request):
    """Education step (Score 2→4)."""
    candidate = get_or_create_candidate_profile(request.user)
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    education_records = EducationHistory.objects.filter(candidate=candidate)

    # Handle deletion
    if request.method == "DELETE":
        delete_id = request.GET.get("delete_id")
        if delete_id:
            EducationHistory.objects.filter(id=delete_id, candidate=candidate).delete()
            # Refresh records
            education_records = EducationHistory.objects.filter(candidate=candidate)

            return render(
                request,
                "candidates/partials/onboarding_education.html",
                {
                    "form": EducationHistoryForm(),
                    "education_records": education_records,
                    "score": user_profile.onboarding_score,
                    "active_tab": "education",
                },
            )

    if request.method == "POST":
        form = EducationHistoryForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.candidate = candidate
            education.save()

            # Update score if at least one education record exists
            if EducationHistory.objects.filter(candidate=candidate).count() >= 1:
                user_profile = update_onboarding_score(request.user, 4)

            # Refresh records
            education_records = EducationHistory.objects.filter(candidate=candidate)
            form = EducationHistoryForm()  # Reset form

            # Reload current partial to allow adding more or continuing
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "candidates/partials/onboarding_education.html",
                    {
                        "form": form,
                        "education_records": education_records,
                        "score": user_profile.onboarding_score,
                        "active_tab": "education",
                    },
                )
            return redirect("candidates:onboarding")
    else:
        form = EducationHistoryForm()

    context = {
        "form": form,
        "education_records": education_records,
        "score": user_profile.onboarding_score,
        "active_tab": "education",
    }

    return render(request, "candidates/partials/onboarding_education.html", context)


@login_required
def onboarding_experience(request):
    """Work experience step (Score 4→6)."""
    candidate = get_or_create_candidate_profile(request.user)
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.candidate = candidate
            experience.save()

            # Update score if at least one experience record exists
            if WorkExperience.objects.filter(candidate=candidate).count() >= 1:
                user_profile = update_onboarding_score(request.user, 6)

            # Reload current partial to allow adding more or continuing
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "candidates/partials/onboarding_experience.html",
                    {
                        "form": WorkExperienceForm(),
                        "work_records": WorkExperience.objects.filter(
                            candidate=candidate
                        ),
                        "score": user_profile.onboarding_score,
                        "active_tab": "experience",
                    },
                )
            return redirect("candidates:onboarding")
    else:
        form = WorkExperienceForm()

    work_records = WorkExperience.objects.filter(candidate=candidate)
    context = {
        "form": form,
        "work_records": work_records,
        "score": user_profile.onboarding_score,
        "active_tab": "experience",
    }

    return render(request, "candidates/partials/onboarding_experience.html", context)


@login_required
def onboarding_targets(request):
    """Target occupations step (Score 6→8)."""
    candidate = get_or_create_candidate_profile(request.user)
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    target_records = OccupationTarget.objects.filter(
        candidate=candidate
    ).select_related("occupation")

    # Handle deletion
    if request.method == "DELETE":
        delete_id = request.GET.get("delete_id")
        if delete_id:
            OccupationTarget.objects.filter(id=delete_id, candidate=candidate).delete()
            # Refresh records
            target_records = OccupationTarget.objects.filter(
                candidate=candidate
            ).select_related("occupation")

            return render(
                request,
                "candidates/partials/onboarding_targets.html",
                {
                    "form": OccupationTargetForm(),
                    "target_records": target_records,
                    "score": user_profile.onboarding_score,
                    "active_tab": "targets",
                    # Recalculate available priorities
                    "available_priorities": [
                        p
                        for p in OccupationTarget.Priority.choices
                        if p[0] not in target_records.values_list("priority", flat=True)
                    ],
                },
            )

    # Calculate available priorities (exclude ones already used)
    used_priorities = set(target_records.values_list("priority", flat=True))
    all_priorities = OccupationTarget.Priority.choices
    available_priorities = [p for p in all_priorities if p[0] not in used_priorities]

    # If POST (add new)
    if request.method == "POST":
        # Check limit
        if target_records.count() >= 3:
            # Just return current list with error or similar - for now just reload
            pass
        else:
            form = OccupationTargetForm(request.POST)
            if form.is_valid():
                target = form.save(commit=False)
                target.candidate = candidate

                # Manual check if priority is used
                if target.priority in used_priorities:
                    form.add_error("priority", "This priority level is already used.")
                else:
                    target.save()

                    # Update score if at least one target exists
                    if (
                        OccupationTarget.objects.filter(candidate=candidate).count()
                        >= 1
                    ):
                        user_profile = update_onboarding_score(request.user, 8)

                    # Refresh records
                    target_records = OccupationTarget.objects.filter(
                        candidate=candidate
                    ).select_related("occupation")
                    used_priorities = set(
                        target_records.values_list("priority", flat=True)
                    )
                    available_priorities = [
                        p for p in all_priorities if p[0] not in used_priorities
                    ]
                    form = OccupationTargetForm()  # Reset form

            # Reload current partial to allow adding more or continuing
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "candidates/partials/onboarding_targets.html",
                    {
                        "form": form,
                        "target_records": target_records,
                        "score": user_profile.onboarding_score,
                        "active_tab": "targets",
                        "available_priorities": available_priorities,
                    },
                )
            return redirect("candidates:onboarding")
    else:
        form = OccupationTargetForm()

    context = {
        "form": form,
        "target_records": target_records,
        "score": user_profile.onboarding_score,
        "active_tab": "targets",
        "available_priorities": available_priorities,
    }

    return render(request, "candidates/partials/onboarding_targets.html", context)


@login_required
def onboarding_assessment(request):
    """Assessment step (Score 8→10)."""
    import random
    from apps.content.models import OccupationTask

    candidate = get_or_create_candidate_profile(request.user)
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    targets = OccupationTarget.objects.filter(candidate=candidate).select_related(
        "occupation"
    )

    tasks = []
    if targets.exists():
        # Priority weights: High(1)=3, Medium(2)=2, Low(3)=1
        priority_weights = {
            OccupationTarget.Priority.HIGH: 3,
            OccupationTarget.Priority.MEDIUM: 2,
            OccupationTarget.Priority.LOW: 1,
        }

        # Calculate partial weights for each target
        target_info = []
        total_weight = 0
        for target in targets:
            w = priority_weights.get(target.priority, 1)
            target_info.append({"target": target, "weight": w, "count": 0})
            total_weight += w

        # Distribute question counts (Max 5)
        MAX_QUESTIONS = 5

        # Sort by weight descending to prioritise high priority targets for remainders
        target_info.sort(key=lambda x: x["weight"], reverse=True)

        remaining_slots = MAX_QUESTIONS

        # First pass: proportional allocation
        if total_weight > 0:
            for item in target_info:
                share = (item["weight"] / total_weight) * MAX_QUESTIONS
                count = int(share)
                item["count"] = count
                remaining_slots -= count

        # Second pass: distribute remainders
        i = 0
        while remaining_slots > 0 and target_info:
            target_info[i % len(target_info)]["count"] += 1
            remaining_slots -= 1
            i += 1

        # Fetch tasks
        for item in target_info:
            if item["count"] > 0:
                # Fetch random tasks for this occupation
                occupation_tasks = list(
                    OccupationTask.objects.filter(occupation=item["target"].occupation)
                    .select_related("occupation")
                    .order_by("?")[: item["count"]]
                )
                tasks.extend(occupation_tasks)

        # Final shuffle
        random.shuffle(tasks)

    if request.method == "POST":
        from .models import AssessmentResponse

        # Save assessment responses
        for key, value in request.POST.items():
            if key.startswith("task_"):
                try:
                    task_id = key.split("_")[1]  # extract ID from task_123
                    task = OccupationTask.objects.get(id=task_id)

                    AssessmentResponse.objects.update_or_create(
                        candidate=candidate, task=task, defaults={"response": value}
                    )
                except (IndexError, OccupationTask.DoesNotExist):
                    continue

        # Mark onboarding as complete
        update_onboarding_score(request.user, 10)

        # Update session to prevent dashboard redirect loop
        request.session["is_onboarded"] = True

        # Ensure candidate stats recompute after onboarding assessment
        candidate.stats_update_needed = True
        candidate.save(update_fields=["stats_update_needed"])

        # Use HTMX redirect to cleanly switch pages
        from django.http import HttpResponse
        from django.urls import reverse

        response = HttpResponse(status=200)
        response["HX-Redirect"] = reverse("user-dashboard")
        return response

    context = {
        "targets": targets,
        "tasks": tasks,
        "score": user_profile.onboarding_score,
        "active_tab": "assessment",
    }
    return render(request, "candidates/partials/onboarding_assessment.html", context)


@login_required
def occupation_assessment(request, occupation_id):
    """
    Comprehensive assessment for a specific target occupation.
    Displays 80% of tasks for thorough proficiency evaluation.
    """
    import random
    from django.http import HttpResponse, Http404
    from django.urls import reverse
    from apps.content.models import Occupation, OccupationTask
    from .models import AssessmentResponse
    from .services import TASK_COVERAGE_PERCENTAGE

    candidate = get_or_create_candidate_profile(request.user)

    # Fetch the occupation and verify it's a user target
    try:
        occupation = Occupation.objects.get(id=occupation_id)
    except Occupation.DoesNotExist:
        raise Http404("Occupation not found")

    # Verify this is one of the candidate's targets
    is_target = OccupationTarget.objects.filter(
        candidate=candidate, occupation=occupation
    ).exists()

    if not is_target:
        # Optionally allow non-target occupations, or redirect
        # For now, we'll allow it but show a warning message
        pass

    # Get all tasks for this occupation
    all_tasks = list(
        OccupationTask.objects.filter(occupation=occupation).select_related(
            "occupation"
        )
    )

    # Calculate how many tasks to show (80%)
    total_count = len(all_tasks)
    required_count = max(1, int(total_count * TASK_COVERAGE_PERCENTAGE))

    # Deterministic random selection based on candidate+occupation
    # This ensures the same candidate always gets the same tasks for this occupation
    random_seed = hash((str(candidate.id), str(occupation.id)))
    random.seed(random_seed)

    # Select random tasks
    if total_count > required_count:
        tasks = random.sample(all_tasks, required_count)
        # Shuffle for variety in presentation
        random.shuffle(tasks)
    else:
        tasks = all_tasks

    # Reset random seed to avoid affecting other code
    random.seed()

    # Get existing responses for progress tracking
    existing_responses = AssessmentResponse.objects.filter(
        candidate=candidate, task__occupation=occupation
    ).values_list("task_id", "response")

    response_dict = dict(existing_responses)

    # Attach existing response to each task for pre-filling the form
    for task in tasks:
        task.existing_response = response_dict.get(task.id, None)

    if request.method == "POST":
        # Save assessment responses
        responses_saved = 0
        for key, value in request.POST.items():
            if key.startswith("task_"):
                try:
                    task_id = key.split("_")[1]
                    task = OccupationTask.objects.get(id=task_id)

                    AssessmentResponse.objects.update_or_create(
                        candidate=candidate, task=task, defaults={"response": value}
                    )
                    responses_saved += 1
                except (IndexError, OccupationTask.DoesNotExist):
                    continue

        # Mark candidate stats for update
        candidate.stats_update_needed = True
        candidate.save()

        # Redirect back to assessments list with success message
        if request.headers.get("HX-Request"):
            response = HttpResponse(status=200)
            response["HX-Redirect"] = reverse("candidates:assessment-list")
            return response

        return redirect("candidates:assessment-list")

    # Calculate completion percentage
    answered_count = len([t for t in tasks if t.existing_response])
    completion_pct = int((answered_count / len(tasks)) * 100) if tasks else 0

    context = navbar_context(request)
    context.update(
        {
            "occupation": occupation,
            "tasks": tasks,
            "is_target": is_target,
            "total_tasks": len(tasks),
            "answered_count": answered_count,
            "completion_pct": completion_pct,
        }
    )

    return render(request, "candidates/occupation_assessment.html", context)


@login_required
def assessment_list(request):
    """List of all available assessments for the candidate."""
    candidate = get_or_create_candidate_profile(request.user)

    # Ensure stats are up to date
    if candidate.stats_update_needed:
        from .services import compute_candidate_stats

        compute_candidate_stats(candidate)

    context = navbar_context(request)
    context.update(
        {
            "assessment_progress": candidate.assessment_progress,
            "recommended_assessments": [
                item
                for item in candidate.recommended_occupations
                if not item.get("is_target")
            ],
        }
    )
    return render(request, "candidates/assessment_list.html", context)


@login_required
def content_feed(request):
    if not hasattr(request.user, "candidate"):
        return redirect("dashboard")

    from apps.core.models import FeatureFlag

    if not FeatureFlag.is_enabled_key("content_feed"):
        return redirect("candidates:assessment-list")

    candidate = request.user.candidate
    occupation_ids = OccupationTarget.objects.filter(candidate=candidate).values_list(
        "occupation_id", flat=True
    )
    media_items = (
        OccupationMedia.objects.filter(
            Q(is_global=True) | Q(occupation_id__in=occupation_ids), is_active=True
        )
        .select_related("occupation")
        .order_by("order", "-created_at")
    )

    paginator = Paginator(media_items, 12)
    page_number = request.GET.get("page")
    media_page = paginator.get_page(page_number)

    context = navbar_context(request)
    context.update(
        {
            "media_items": media_page,
            "has_targets": occupation_ids.exists(),
        }
    )
    return render(request, "candidates/content_feed.html", context)


@login_required
def content_feed_detail(request, media_id):
    if not hasattr(request.user, "candidate"):
        return redirect("dashboard")

    from apps.core.models import FeatureFlag

    if not FeatureFlag.is_enabled_key("content_feed"):
        return redirect("candidates:assessment-list")

    candidate = request.user.candidate
    occupation_ids = OccupationTarget.objects.filter(candidate=candidate).values_list(
        "occupation_id", flat=True
    )
    media_item = get_object_or_404(
        OccupationMedia,
        Q(is_global=True) | Q(occupation_id__in=occupation_ids),
        is_active=True,
        pk=media_id,
    )

    page_param = request.GET.get("page")
    back_url = reverse("candidates:content-feed")
    if page_param:
        back_url = f"{back_url}?page={page_param}"

    context = navbar_context(request)
    context.update({"media_item": media_item, "back_url": back_url})
    return render(request, "candidates/content_feed_detail.html", context)


@login_required
@user_passes_test(is_admin_or_super_admin)
def candidate_list(request):
    query = request.GET.get("q", "")
    candidates = CandidateProfile.objects.select_related("user").all()

    if query:
        candidates = candidates.filter(user__email__icontains=query)

    context = navbar_context(request)
    context.update({"candidates": candidates, "search_query": query})
    return render(request, "candidates/candidate_list.html", context)


@login_required
@user_passes_test(is_admin_or_super_admin)
def candidate_add(request):
    if request.method == "POST":
        form = CandidateCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("candidate-list")
    else:
        form = CandidateCreateForm()

    context = navbar_context(request)
    context["form"] = form
    return render(request, "candidates/candidate_form.html", context)


@login_required
@user_passes_test(is_admin_or_super_admin)
def candidate_edit_dashboard(request, candidate_id):
    """Main candidate edit dashboard with side navigation."""
    candidate = get_object_or_404(CandidateProfile, pk=candidate_id)

    context = navbar_context(request)
    context.update(
        {
            "candidate": candidate,
            "active_section": "profile",
            "active_section_url": reverse(
                "candidates:candidate-edit-profile",
                kwargs={"candidate_id": candidate_id},
            ),
        }
    )
    return render(request, "candidates/candidate_edit_dashboard.html", context)


@login_required
@user_passes_test(is_admin_or_super_admin)
def candidate_edit_profile(request, candidate_id):
    """Edit candidate basic profile information."""
    candidate = get_object_or_404(CandidateProfile, pk=candidate_id)
    user = candidate.user

    if request.method == "POST":
        # Update user fields
        user.first_name = request.POST.get("first_name", "")
        user.last_name = request.POST.get("last_name", "")
        user.email = request.POST.get("email", "")
        user.save()

        # Update candidate profile if needed
        candidate.save()

        messages.success(request, "Profile updated successfully!")
        if request.headers.get("HX-Request"):
            context = navbar_context(request)
            context.update(
                {
                    "candidate": candidate,
                    "active_section": "profile",
                    "active_section_url": reverse(
                        "candidates:candidate-edit-profile",
                        kwargs={"candidate_id": candidate_id},
                    ),
                }
            )
            return render(request, "candidates/partials/edit_profile.html", context)
        return redirect("candidates:candidate-edit-profile", candidate_id=candidate_id)

    context = navbar_context(request)
    context.update(
        {
            "candidate": candidate,
            "active_section": "profile",
            "active_section_url": reverse(
                "candidates:candidate-edit-profile",
                kwargs={"candidate_id": candidate_id},
            ),
        }
    )
    return render(request, "candidates/partials/edit_profile.html", context)


@login_required
@user_passes_test(is_admin_or_super_admin)
def candidate_edit_education(request, candidate_id):
    """Edit candidate education history."""
    candidate = get_object_or_404(CandidateProfile, pk=candidate_id)
    education_records = candidate.education_history.all()

    if request.method == "POST":
        delete_id = request.POST.get("delete_id")
        if delete_id:
            EducationHistory.objects.filter(id=delete_id, candidate=candidate).delete()
            messages.success(request, "Education record removed successfully!")
        else:
            form = EducationHistoryForm(request.POST)
            if form.is_valid():
                education = form.save(commit=False)
                education.candidate = candidate
                education.save()
                messages.success(request, "Education record added successfully!")
        if request.headers.get("HX-Request"):
            education_records = candidate.education_history.all()
        else:
            return redirect(
                "candidates:candidate-edit-education", candidate_id=candidate_id
            )
    else:
        form = EducationHistoryForm()

    context = navbar_context(request)
    context.update(
        {
            "candidate": candidate,
            "active_section": "education",
            "active_section_url": reverse(
                "candidates:candidate-edit-education",
                kwargs={"candidate_id": candidate_id},
            ),
            "form": form,
            "education_records": education_records,
        }
    )
    return render(request, "candidates/partials/edit_education.html", context)


@login_required
@user_passes_test(is_admin_or_super_admin)
def candidate_edit_experience(request, candidate_id):
    """Edit candidate work experience."""
    candidate = get_object_or_404(CandidateProfile, pk=candidate_id)
    work_records = candidate.work_experience.all()

    if request.method == "POST":
        delete_id = request.POST.get("delete_id")
        if delete_id:
            WorkExperience.objects.filter(id=delete_id, candidate=candidate).delete()
            messages.success(request, "Work experience removed successfully!")
        else:
            form = WorkExperienceForm(request.POST)
            if form.is_valid():
                experience = form.save(commit=False)
                experience.candidate = candidate
                experience.save()
                messages.success(request, "Work experience added successfully!")
        if request.headers.get("HX-Request"):
            work_records = candidate.work_experience.all()
        else:
            return redirect(
                "candidates:candidate-edit-experience", candidate_id=candidate_id
            )
    else:
        form = WorkExperienceForm()

    context = navbar_context(request)
    context.update(
        {
            "candidate": candidate,
            "active_section": "experience",
            "active_section_url": reverse(
                "candidates:candidate-edit-experience",
                kwargs={"candidate_id": candidate_id},
            ),
            "form": form,
            "work_records": work_records,
        }
    )
    return render(request, "candidates/partials/edit_experience.html", context)


@login_required
@user_passes_test(is_admin_or_super_admin)
def candidate_edit_targets(request, candidate_id):
    """Edit candidate occupation targets."""
    candidate = get_object_or_404(CandidateProfile, pk=candidate_id)
    target_records = candidate.occupation_targets.select_related("occupation").all()

    # Calculate available priorities
    used_priorities = set(target_records.values_list("priority", flat=True))
    all_priorities = OccupationTarget.Priority.choices
    available_priorities = [p for p in all_priorities if p[0] not in used_priorities]

    if request.method == "POST":
        delete_id = request.POST.get("delete_id")
        if delete_id:
            OccupationTarget.objects.filter(id=delete_id, candidate=candidate).delete()
            messages.success(request, "Occupation target removed successfully!")
        else:
            if target_records.count() >= 3:
                messages.error(request, "Maximum 3 occupation targets allowed.")
            else:
                form = OccupationTargetForm(request.POST)
                if form.is_valid():
                    target = form.save(commit=False)
                    target.candidate = candidate

                    if target.priority in used_priorities:
                        form.add_error(
                            "priority", "This priority level is already used."
                        )
                    else:
                        target.save()
                        messages.success(
                            request, "Occupation target added successfully!"
                        )
        if request.headers.get("HX-Request"):
            target_records = candidate.occupation_targets.select_related(
                "occupation"
            ).all()
            used_priorities = set(target_records.values_list("priority", flat=True))
            available_priorities = [
                p for p in all_priorities if p[0] not in used_priorities
            ]
        else:
            return redirect(
                "candidates:candidate-edit-targets", candidate_id=candidate_id
            )
    else:
        form = OccupationTargetForm()

    context = navbar_context(request)
    context.update(
        {
            "candidate": candidate,
            "active_section": "targets",
            "active_section_url": reverse(
                "candidates:candidate-edit-targets",
                kwargs={"candidate_id": candidate_id},
            ),
            "form": form,
            "target_records": target_records,
            "available_priorities": available_priorities,
        }
    )
    return render(request, "candidates/partials/edit_targets.html", context)


@login_required
@user_passes_test(is_admin_or_super_admin)
def candidate_edit_assessments(request, candidate_id):
    """View candidate assessment progress and responses."""
    candidate = get_object_or_404(CandidateProfile, pk=candidate_id)
    assessment_responses = candidate.assessment_responses.select_related(
        "task", "task__occupation"
    ).all()

    # Group responses by occupation
    responses_by_occupation = {}
    for response in assessment_responses:
        occupation = response.task.occupation
        if occupation not in responses_by_occupation:
            responses_by_occupation[occupation] = []
        responses_by_occupation[occupation].append(response)

    context = navbar_context(request)
    context.update(
        {
            "candidate": candidate,
            "active_section": "assessments",
            "active_section_url": reverse(
                "candidates:candidate-edit-assessments",
                kwargs={"candidate_id": candidate_id},
            ),
            "assessment_responses": assessment_responses,
            "responses_by_occupation": responses_by_occupation,
        }
    )
    return render(request, "candidates/partials/edit_assessments.html", context)


@login_required
@user_passes_test(is_admin_or_super_admin)
def candidate_edit_files(request, candidate_id):
    """Edit candidate file attachments."""
    candidate = get_object_or_404(CandidateProfile, pk=candidate_id)

    if request.method == "POST":
        files = request.POST.getlist("files")
        candidate.files.set(files)
        candidate.save()
        messages.success(request, "Files updated successfully!")
        return redirect("candidates:candidate-edit-files", candidate_id=candidate_id)

    context = navbar_context(request)
    context.update(
        {
            "candidate": candidate,
            "active_section": "files",
            "active_section_url": reverse(
                "candidates:candidate-edit-files",
                kwargs={"candidate_id": candidate_id},
            ),
        }
    )
    return render(request, "candidates/partials/edit_files.html", context)


@login_required
@user_passes_test(is_admin_or_super_admin)
def candidate_mark_stats_recompute(request, candidate_id):
    """Mark candidate stats for recompute."""
    candidate = get_object_or_404(CandidateProfile, pk=candidate_id)
    if request.method == "POST":
        candidate.stats_update_needed = True
        candidate.save(update_fields=["stats_update_needed"])
        messages.success(request, "Candidate status marked for recompute.")

    context = navbar_context(request)
    context.update(
        {
            "candidate": candidate,
            "active_section": "profile",
            "active_section_url": reverse(
                "candidates:candidate-edit-profile",
                kwargs={"candidate_id": candidate_id},
            ),
        }
    )
    if request.headers.get("HX-Request"):
        response = HttpResponse(status=200)
        response["HX-Redirect"] = reverse(
            "candidates:candidate-edit", kwargs={"candidate_id": candidate_id}
        )
        return response
    return redirect("candidates:candidate-edit", candidate_id=candidate_id)


@login_required
@user_passes_test(is_admin_or_super_admin)
def candidate_delete(request, candidate_id):
    candidate = get_object_or_404(CandidateProfile, pk=candidate_id)
    if request.method == "POST" or request.method == "DELETE":
        candidate.delete()
        return redirect("candidate-list")

    context = navbar_context(request)
    context["candidate"] = candidate
    return render(request, "candidates/candidate_confirm_delete.html", context)
