from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.accounts.models import UserProfile
from apps.core.context_processors import navbar_context

from .forms import (
    EducationHistoryForm,
    OccupationTargetForm,
    ProfileForm,
    WorkExperienceForm,
)
from .models import CandidateProfile, EducationHistory, OccupationTarget, WorkExperience


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
    context.update({
        "onboarding_score": score,
        "active_tab": active_tab,
    })

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
                    {"form": EducationHistoryForm(), "score": user_profile.onboarding_score, "active_tab": "education"},
                )
            return redirect("candidates:onboarding")
    else:
        form = ProfileForm(initial={"first_name": request.user.first_name, "last_name": request.user.last_name})

    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "candidates/partials/onboarding_profile.html", {"form": form, "score": user_profile.onboarding_score, "active_tab": "profile"})


@login_required
def onboarding_education(request):
    """Education step (Score 2→4)."""
    candidate = get_or_create_candidate_profile(request.user)
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = EducationHistoryForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.candidate = candidate
            education.save()

            # Update score if at least one education record exists
            if EducationHistory.objects.filter(candidate=candidate).count() >= 1:
                user_profile = update_onboarding_score(request.user, 4)

            # Reload current partial to allow adding more or continuing
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "candidates/partials/onboarding_education.html",
                    {
                        "form": EducationHistoryForm(), 
                        "education_records": EducationHistory.objects.filter(candidate=candidate),
                        "score": user_profile.onboarding_score, 
                        "active_tab": "education"
                    },
                )
            return redirect("candidates:onboarding")
    else:
        form = EducationHistoryForm()

    education_records = EducationHistory.objects.filter(candidate=candidate)
    context = {"form": form, "education_records": education_records, "score": user_profile.onboarding_score, "active_tab": "education"}

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
                        "work_records": WorkExperience.objects.filter(candidate=candidate),
                        "score": user_profile.onboarding_score, 
                        "active_tab": "experience"
                    },
                )
            return redirect("candidates:onboarding")
    else:
        form = WorkExperienceForm()

    work_records = WorkExperience.objects.filter(candidate=candidate)
    context = {"form": form, "work_records": work_records, "score": user_profile.onboarding_score, "active_tab": "experience"}

    return render(request, "candidates/partials/onboarding_experience.html", context)


@login_required
def onboarding_targets(request):
    """Target occupations step (Score 6→8)."""
    candidate = get_or_create_candidate_profile(request.user)
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = OccupationTargetForm(request.POST)
        if form.is_valid():
            target = form.save(commit=False)
            target.candidate = candidate
            target.save()

            # Update score if at least one target exists
            if OccupationTarget.objects.filter(candidate=candidate).count() >= 1:
                user_profile = update_onboarding_score(request.user, 8)

            # Reload current partial to allow adding more or continuing
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "candidates/partials/onboarding_targets.html",
                    {
                        "form": OccupationTargetForm(),
                        "target_records": OccupationTarget.objects.filter(candidate=candidate).select_related("occupation"),
                        "score": user_profile.onboarding_score,
                        "active_tab": "targets"
                    },
                )
            return redirect("candidates:onboarding")
    else:
        form = OccupationTargetForm()

    target_records = OccupationTarget.objects.filter(candidate=candidate).select_related("occupation")
    context = {"form": form, "target_records": target_records, "score": user_profile.onboarding_score, "active_tab": "targets"}

    return render(request, "candidates/partials/onboarding_targets.html", context)


@login_required
def onboarding_assessment(request):
    """Assessment step (Score 8→10)."""
    import random
    from apps.content.models import OccupationTask

    candidate = get_or_create_candidate_profile(request.user)
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    targets = OccupationTarget.objects.filter(candidate=candidate).select_related("occupation")

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
                occupation_tasks = list(OccupationTask.objects.filter(
                    occupation=item["target"].occupation
                ).select_related('occupation').order_by('?')[:item["count"]])
                tasks.extend(occupation_tasks)
        
        # Final shuffle
        random.shuffle(tasks)

    if request.method == "POST":
        from .models import AssessmentResponse
        
        # Save assessment responses
        for key, value in request.POST.items():
            if key.startswith("task_"):
                try:
                    task_id = key.split("_")[1] # extract ID from task_123
                    task = OccupationTask.objects.get(id=task_id)
                    
                    AssessmentResponse.objects.update_or_create(
                        candidate=candidate,
                        task=task,
                        defaults={"response": value}
                    )
                except (IndexError, OccupationTask.DoesNotExist):
                    continue

        # Mark onboarding as complete
        update_onboarding_score(request.user, 10)
        
        # Update session to prevent dashboard redirect loop
        request.session["is_onboarded"] = True
        
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
        "active_tab": "assessment"
    }
    return render(request, "candidates/partials/onboarding_assessment.html", context)
