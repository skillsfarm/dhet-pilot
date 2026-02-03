from django import forms
from .models import Occupation, OccupationTask, Industry

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
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

class OccupationTaskForm(forms.ModelForm):
    class Meta:
        model = OccupationTask
        fields = ["title", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }
