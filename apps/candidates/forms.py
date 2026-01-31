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
            "occupation": forms.Select(attrs={"class": "app-input"}),
            "priority": forms.Select(attrs={"class": "app-input"}),
        }
