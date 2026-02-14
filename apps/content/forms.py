from django import forms
from django.core.exceptions import ValidationError

from .models import Occupation, OccupationTask, Industry, Skill, OccupationMedia


class OccupationForm(forms.ModelForm):
    class Meta:
        model = Occupation
        fields = [
            "ofo_code",
            "ofo_title",
            "description",
            "industry",
            "years_of_experience",
            "preferred_nqf_level",
            "files",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "files": forms.CheckboxSelectMultiple(),
        }


class IndustryForm(forms.ModelForm):
    class Meta:
        model = Industry
        fields = ["code", "name", "description"]
        widgets = {
            "code": forms.TextInput(attrs={"class": "app-input w-full"}),
            "name": forms.TextInput(attrs={"class": "app-input w-full"}),
            "description": forms.Textarea(
                attrs={"class": "app-input w-full", "rows": 4}
            ),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "app-input"}),
            "description": forms.Textarea(attrs={"class": "app-input", "rows": 4}),
        }


class OccupationTaskForm(forms.ModelForm):
    class Meta:
        model = OccupationTask
        fields = ["title", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class OccupationMediaForm(forms.ModelForm):
    """Form for managing occupation multimedia content."""

    class Meta:
        model = OccupationMedia
        fields = [
            "title",
            "description",
            "media_type",
            "source_type",
            "remote_url",
            "embed_code",
            "local_file",
            "order",
            "is_featured",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "app-input"}),
            "description": forms.Textarea(attrs={"class": "app-input", "rows": 3}),
            "media_type": forms.Select(attrs={"class": "app-input"}),
            "source_type": forms.Select(attrs={"class": "app-input"}),
            "remote_url": forms.URLInput(attrs={"class": "app-input"}),
            "embed_code": forms.Textarea(attrs={"class": "app-input", "rows": 4}),
            "local_file": forms.Select(attrs={"class": "app-input"}),
            "order": forms.NumberInput(attrs={"class": "app-input"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "app-checkbox"}),
            "is_active": forms.CheckboxInput(attrs={"class": "app-checkbox"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["source_type"].initial = OccupationMedia.SourceType.REMOTE

        from apps.storage.models import File

        self.fields["local_file"].queryset = File.objects.filter(
            mimetype__in=[
                "video/mp4",
                "video/webm",
                "video/ogg",
                "application/pdf",
                "image/jpeg",
                "image/png",
                "image/gif",
                "image/webp",
                "audio/mpeg",
                "audio/ogg",
                "audio/wav",
            ]
        ).order_by("-created_at")

    def clean(self):
        cleaned_data = super().clean()
        source_type = cleaned_data.get("source_type")
        remote_url = cleaned_data.get("remote_url")
        embed_code = cleaned_data.get("embed_code")
        local_file = cleaned_data.get("local_file")

        if source_type == OccupationMedia.SourceType.REMOTE:
            if not remote_url and not embed_code:
                raise ValidationError(
                    "Provide a remote URL or embed code for remote media."
                )

        if source_type == OccupationMedia.SourceType.LOCAL and not local_file:
            raise ValidationError("Select a local file for local media.")

        return cleaned_data
