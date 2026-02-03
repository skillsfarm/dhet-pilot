from django import forms
from django.contrib.auth import get_user_model

from .models import CandidateProfile, EducationHistory, OccupationTarget, WorkExperience

User = get_user_model()


class ProfileForm(forms.ModelForm):
    """Form for updating user's basic profile information."""

    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        if self.user:
            self.user.first_name = self.cleaned_data["first_name"]
            self.user.last_name = self.cleaned_data["last_name"]
            if commit:
                self.user.save()
        return self.user


class EducationHistoryForm(forms.ModelForm):
    """Form for adding educational background."""

    class Meta:
        model = EducationHistory
        fields = ["education_type", "institution", "field_of_study", "year_completed"]
        widgets = {
            "education_type": forms.Select(attrs={"class": "app-input"}),
            "institution": forms.TextInput(
                attrs={"class": "app-input", "placeholder": "Institution name"}
            ),
            "field_of_study": forms.TextInput(
                attrs={"class": "app-input", "placeholder": "Field of study (optional)"}
            ),
            "year_completed": forms.NumberInput(
                attrs={"class": "app-input", "placeholder": "Year completed"}
            ),
        }


class WorkExperienceForm(forms.ModelForm):
    """Form for adding work experience."""

    class Meta:
        model = WorkExperience
        fields = ["job_title", "company", "start_date", "end_date"]
        widgets = {
            "job_title": forms.TextInput(
                attrs={"class": "app-input", "placeholder": "Job title"}
            ),
            "company": forms.TextInput(
                attrs={"class": "app-input", "placeholder": "Company name"}
            ),
            "start_date": forms.DateInput(
                attrs={"class": "app-input", "type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={
                    "class": "app-input",
                    "type": "date",
                    "placeholder": "Leave blank if current",
                }
            ),
        }


class OccupationTargetForm(forms.ModelForm):
    """Form for selecting target occupations."""

    class Meta:
        model = OccupationTarget
        fields = ["occupation", "priority"]
        widgets = {
            "occupation": forms.Select(attrs={"class": "app-input app-select2"}),
            "priority": forms.Select(attrs={"class": "app-input"}),
        }

    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop("candidate", None)
        super().__init__(*args, **kwargs)

        if self.candidate:
            # 1. Filter Occupations
            # Get IDs of occupations already targeted by this candidate
            # If we are editing an existing instance, exclude it from the "already targeted" list (though usually we don't change occupation on edit)
            existing_targets_query = OccupationTarget.objects.filter(candidate=self.candidate)
            if self.instance and self.instance.pk:
                existing_targets_query = existing_targets_query.exclude(pk=self.instance.pk)
            
            taken_occupation_ids = existing_targets_query.values_list("occupation_id", flat=True)
            
            if taken_occupation_ids:
                # Filter the queryset of the 'occupation' field
                self.fields["occupation"].queryset = self.fields["occupation"].queryset.exclude(
                    id__in=taken_occupation_ids
                )

            # 2. Filter Priorities
            # Get priorities already taken
            taken_priorities = existing_targets_query.values_list("priority", flat=True)
            
            if taken_priorities:
                # Remove taken priorities from choices
                # 'priority' is a ChoiceField (or derived from model choices)
                # We need to reconstruct choices provided by the model field
                current_choices = self.fields["priority"].choices
                new_choices = [
                    choice for choice in current_choices 
                    if choice[0] not in taken_priorities and choice[0] != ""
                ]
                # Ensure we have a placeholder if there are choices left, or if empty (though logic might handle empty differently)
                # Note: ChoiceField internal logic is a bit complex with empty values.
                # Safest bet for a required field with dynamic choices is to ensure no default is pre-selected if we want forced choice,
                # but 'Select Priority' is good UX.
                # However, since we are REPLACING choices, we must be careful.
                # The model field choices likely don't have an empty option.
                # Let's add one.
                final_choices = [("", "Select Priority")] + new_choices
                self.fields["priority"].choices = final_choices
