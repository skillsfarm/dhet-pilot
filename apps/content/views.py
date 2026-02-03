from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse

from apps.core.context_processors import navbar_context
from .models import Occupation, OccupationTask
from .forms import OccupationForm, OccupationTaskForm

def is_staff_or_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_staff_or_admin)
def occupation_edit(request, occupation_id):
    """
    Main view for editing an occupation.
    Renders the page shell which loads partials via HTMX? 
    Strictly following the profile pattern, the main view loads the page with the first tab content pre-loaded or ready to load.
    Here we'll load the full page with the details form ready.
    """
    occupation = get_object_or_404(Occupation, pk=occupation_id)
    
    # We can just render the template. The template will include the 
    # partials or use hx-trigger="load" to fetch them.
    # profile.html uses hx-trigger="load" for the tab content.
    
    context = navbar_context(request)
    context["occupation"] = occupation
    return render(request, "content/occupation_edit.html", context)

@login_required
@user_passes_test(is_staff_or_admin)
def occupation_details_partial(request, occupation_id):
    """
    HTMX partial for editing occupation details.
    """
    occupation = get_object_or_404(Occupation, pk=occupation_id)
    
    if request.method == "POST":
        form = OccupationForm(request.POST, instance=occupation)
        if form.is_valid():
            form.save()
            messages.success(request, "Occupation details updated successfully!")
    else:
        form = OccupationForm(instance=occupation)
        
    context = {"form": form, "occupation": occupation}
    return render(request, "content/partials/occupation_details.html", context)

@login_required
@user_passes_test(is_staff_or_admin)
def occupation_tasks_partial(request, occupation_id):
    """
    HTMX partial for listing and adding tasks.
    """
    occupation = get_object_or_404(Occupation, pk=occupation_id)
    
    if request.method == "POST":
        form = OccupationTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.occupation = occupation
            task.save()
            messages.success(request, "Task created successfully!")
            form = OccupationTaskForm() # Reset form
    else:
        form = OccupationTaskForm()
        
    tasks = occupation.tasks.all()
    
    context = {
        "form": form,
        "occupation": occupation,
        "tasks": tasks
    }
    return render(request, "content/partials/occupation_tasks.html", context)

@login_required
@user_passes_test(is_staff_or_admin)
def occupation_task_detail(request, occupation_id, task_id):
    """
    HTMX partial for editing/deleting a single task.
    """
    occupation = get_object_or_404(Occupation, pk=occupation_id)
    task = get_object_or_404(OccupationTask, pk=task_id, occupation=occupation)
    
    if request.method == "DELETE":
        task.delete()
        messages.success(request, "Task deleted.")
        return HttpResponse("") # Client side should remove the row

    # Editing (using GET with ?mode=edit or pure POST)
    # The profile example uses a query param ?mode=edit to switch to edit mode
    
    start_editing = request.GET.get("mode") == "edit"

    if request.method == "POST":
        form = OccupationTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated.")
            start_editing = False # Exit edit mode
    else:
        # GET request, possibly just viewing or fetching form for edit
        form = OccupationTaskForm(instance=task)

    context = {
        "task": task,
        "form": form if start_editing else None, # Only pass form if editing
        "start_editing": start_editing,
        "occupation": occupation,
    }
    return render(request, "content/partials/item_task.html", context)
