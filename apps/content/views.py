from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
import csv
import io


from apps.core.context_processors import navbar_context
from .models import Occupation, OccupationTask, Industry
from .forms import OccupationForm, OccupationTaskForm


from rolepermissions.checkers import has_role


def is_staff_or_admin(user):
    return (
        user.is_staff
        or user.is_superuser
        or has_role(user, ["content_manager", "admin", "super_admin"])
    )


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
            form = OccupationTaskForm()  # Reset form
    else:
        form = OccupationTaskForm()

    tasks = occupation.tasks.all()

    context = {"form": form, "occupation": occupation, "tasks": tasks}
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
        return HttpResponse("")  # Client side should remove the row

    # Editing (using GET with ?mode=edit or pure POST)
    # The profile example uses a query param ?mode=edit to switch to edit mode

    start_editing = request.GET.get("mode") == "edit"

    if request.method == "POST":
        form = OccupationTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated.")
            start_editing = False  # Exit edit mode
    else:
        # GET request, possibly just viewing or fetching form for edit
        form = OccupationTaskForm(instance=task)

    context = {
        "task": task,
        "form": form if start_editing else None,  # Only pass form if editing
        "start_editing": start_editing,
        "occupation": occupation,
    }
    return render(request, "content/partials/item_task.html", context)


@login_required
@user_passes_test(is_staff_or_admin)
def occupation_add(request):
    """
    View to add a single occupation with tasks and potentially a new industry.
    """
    if request.method == "POST":
        form = OccupationForm(request.POST)

        # Handle dynamic industry name if it doesn't exist as an ID
        industry_input = request.POST.get("industry_name")
        industry_id = request.POST.get("industry")

        if not industry_id and industry_input:
            # Try to find industry by name or create it
            industry, created = Industry.objects.get_or_create(
                name=industry_input,
                defaults={"code": industry_input.upper().replace(" ", "_")[:50]},
            )
            # Link it to the form data
            data = request.POST.copy()
            data["industry"] = industry.id
            form = OccupationForm(data)

        if form.is_valid():
            occupation = form.save()

            # Handle tasks
            task_titles = request.POST.getlist("task_titles[]")
            task_descriptions = request.POST.getlist("task_descriptions[]")

            for title, desc in zip(task_titles, task_descriptions):
                if title.strip():
                    OccupationTask.objects.create(
                        occupation=occupation,
                        title=title.strip(),
                        description=desc.strip(),
                    )

            messages.success(request, "Occupation created successfully with tasks!")
            return redirect("occupation-edit", occupation_id=occupation.id)
    else:
        form = OccupationForm()

    # Get some industries for autocomplete
    industries = Industry.objects.all().values("id", "name")[:20]

    # Get some common tasks for autocomplete (title and description)
    common_tasks = list(
        OccupationTask.objects.values("title", "description").distinct()[:50]
    )

    import json

    context = navbar_context(request)
    context["form"] = form
    context["industries_json"] = json.dumps(list(industries))
    context["common_tasks_json"] = json.dumps(list(common_tasks))
    context["nqf_levels"] = [
        {"id": "0", "name": "Any / Not Applicable (0)"},
        {"id": "4", "name": "Grade 12 / Matric (4)"},
        {"id": "5", "name": "Higher Certificate (5)"},
        {"id": "6", "name": "Diploma / Advanced Certificate (6)"},
        {"id": "7", "name": "Bachelor's Degree / Advanced Diploma (7)"},
        {"id": "8", "name": "Honours Degree / PG Diploma (8)"},
        {"id": "9", "name": "Master's Degree (9)"},
        {"id": "10", "name": "Doctoral Degree (10)"},
    ]
    return render(request, "content/occupation_add.html", context)


@login_required
@user_passes_test(is_staff_or_admin)
def occupation_upload(request):
    """
    View to bulk upload occupations via CSV.
    """
    if request.method == "POST":
        csv_file = request.FILES.get("file")
        if not csv_file:
            messages.error(request, "Please upload a CSV file.")
        elif not csv_file.name.endswith(".csv"):
            messages.error(request, "File is not CSV.")
        else:
            try:
                data_set = csv_file.read().decode("UTF-8")
                io_string = io.StringIO(data_set)
                reader = csv.reader(io_string, delimiter=",", quotechar='"')

                next(reader, None)

                count = 0
                for column in reader:
                    # Expecting: ofo_code, ofo_title, description, industry_code, years_of_experience, preferred_nqf_level
                    if len(column) < 2:
                        continue

                    ofo_code = column[0].strip()
                    ofo_title = column[1].strip()
                    description = column[2].strip() if len(column) > 2 else ""
                    industry_code = column[3].strip() if len(column) > 3 else None
                    years_of_experience = (
                        int(column[4])
                        if len(column) > 4 and column[4].strip().isdigit()
                        else 0
                    )
                    preferred_nqf_level = (
                        int(column[5])
                        if len(column) > 5 and column[5].strip().isdigit()
                        else 0
                    )

                    industry = None
                    if industry_code:
                        industry = Industry.objects.filter(code=industry_code).first()

                    Occupation.objects.update_or_create(
                        ofo_code=ofo_code,
                        defaults={
                            "ofo_title": ofo_title,
                            "description": description,
                            "industry": industry,
                            "years_of_experience": years_of_experience,
                            "preferred_nqf_level": preferred_nqf_level,
                        },
                    )
                    count += 1
                messages.success(request, f"Successfully uploaded {count} occupations.")
                return redirect("occupations")
            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")

    context = navbar_context(request)
    return render(request, "content/occupation_upload.html", context)


@login_required
@user_passes_test(is_staff_or_admin)
def occupation_delete(request, occupation_id):
    """
    View to delete an occupation.
    """
    occupation = get_object_or_404(Occupation, pk=occupation_id)
    if request.method == "POST" or request.method == "DELETE":
        occupation.delete()
        messages.success(request, "Occupation deleted successfully.")
        return redirect("occupations")

    context = navbar_context(request)
    context["occupation"] = occupation
    return render(request, "content/occupation_confirm_delete.html", context)


@login_required
@user_passes_test(is_staff_or_admin)
def occupation_bulk_delete(request):
    """
    View to delete multiple occupations.
    """
    if request.method == "POST":
        occupation_ids = request.POST.getlist("selected_occupations")
        if occupation_ids:
            deleted_count = Occupation.objects.filter(id__in=occupation_ids).delete()[0]
            messages.success(
                request,
                f"Successfully deleted {deleted_count} occupations related records.",
            )
        else:
            messages.warning(request, "No occupations selected for deletion.")
    return redirect("occupations")


@login_required
def task_list_partial(request):
    """
    HTMX view to return a list of tasks for the search modal.
    """
    from django.db.models import Q
    from django.core.paginator import Paginator

    query = request.GET.get("q", "")
    tasks_qs = (
        OccupationTask.objects.values("id", "title", "description")
        .distinct()
        .order_by("title")
    )

    if query:
        tasks_qs = tasks_qs.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    paginator = Paginator(tasks_qs, 10)
    page_number = request.GET.get("page")
    tasks_page = paginator.get_page(page_number)

    return render(
        request,
        "content/partials/task_list_selector.html",
        {"tasks": tasks_page, "search_query": query},
    )
