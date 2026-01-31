from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import CuidModel


class CandidateProfile(CuidModel):
    """
    Extended profile for candidates (average users of the platform).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="candidate"
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Candidate Profile"
        verbose_name_plural = "Candidate Profiles"

    def __str__(self):
        return f"{self.user.username}'s candidate profile"

    # Computed Stats
    highest_nqf_level = models.CharField(max_length=50, blank=True, help_text="Cached highest NQF level")
    occupation_matches_count = models.PositiveIntegerField(default=0, help_text="Number of occupation matches found")
    recommended_occupations = models.JSONField(default=list, blank=True, help_text="List of recommended occupation IDs or details")
    assessment_progress = models.JSONField(default=dict, blank=True, help_text="Progress stats per occupation")
    
    # Flags
    stats_update_needed = models.BooleanField(default=True, help_text="Flag to trigger stats re-computation")
    stats_last_computed = models.DateTimeField(null=True, blank=True)


class EducationHistory(CuidModel):
    """
    Educational background of a candidate.
    """

    class EducationType(models.TextChoices):
        MATRIC = "MATRIC", "Matric (Grade 12)"
        CERTIFICATE = "CERTIFICATE", "Certificate"
        DIPLOMA = "DIPLOMA", "Diploma"
        DEGREE = "DEGREE", "Bachelor's Degree"
        HONORS = "HONORS", "Honours Degree"
        MASTERS = "MASTERS", "Master's Degree"
        DOCTORATE = "DOCTORATE", "Doctorate"

    candidate = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="education_history"
    )
    education_type = models.CharField(
        max_length=20, choices=EducationType.choices, default=EducationType.MATRIC
    )
    institution = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255, blank=True)
    year_completed = models.PositiveIntegerField()

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Education History"
        verbose_name_plural = "Education Histories"
        ordering = ["-year_completed"]

    def __str__(self):
        return f"{self.candidate.user.username} - {self.get_education_type_display()} ({self.year_completed})"


class WorkExperience(CuidModel):
    """
    Work experience of a candidate.
    """

    candidate = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="work_experience"
    )
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank if current position")
    tasks = models.ManyToManyField(
        "content.OccupationTask", related_name="work_experiences", blank=True
    )
    skills = models.ManyToManyField(
        "content.Skill", related_name="work_experiences", blank=True
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Work Experience"
        verbose_name_plural = "Work Experiences"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.candidate.user.username} - {self.job_title} at {self.company}"

    @property
    def years_experience(self):
        """Calculate years of experience."""
        from datetime import date

        end = self.end_date or date.today()
        delta = end - self.start_date
        return round(delta.days / 365.25, 1)


class OccupationTarget(CuidModel):
    """
    Target occupations that a candidate is interested in.
    Candidates must have at least 1 target with 3 priority levels.
    """

    class Priority(models.IntegerChoices):
        HIGH = 1, "High Priority"
        MEDIUM = 2, "Medium Priority"
        LOW = 3, "Low Priority"

    candidate = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="occupation_targets"
    )
    occupation = models.ForeignKey(
        "content.Occupation", on_delete=models.CASCADE, related_name="candidate_targets"
    )
    priority = models.IntegerField(choices=Priority.choices, default=Priority.HIGH)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Occupation Target"
        verbose_name_plural = "Occupation Targets"
        unique_together = ["candidate", "occupation"]
        ordering = ["priority", "occupation__ofo_code"]

    def __str__(self):
        return f"{self.candidate.user.username} → {self.occupation.ofo_title} (Priority {self.priority})"


class AssessmentResponse(CuidModel):
    """
    Stores a candidate's response to an assessment task.
    """
    class ResponseType(models.TextChoices):
        YES = "yes", "Yes, I have done this"
        PARTIALLY = "partially", "Partially / Sometimes"
        NO = "no", "No, never"

    candidate = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="assessment_responses"
    )
    task = models.ForeignKey(
        "content.OccupationTask", on_delete=models.CASCADE, related_name="candidate_responses"
    )
    response = models.CharField(max_length=20, choices=ResponseType.choices)
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Assessment Response"
        verbose_name_plural = "Assessment Responses"
        unique_together = ["candidate", "task"]

    def __str__(self):
        return f"{self.candidate.user.username} - {self.task.title}: {self.response}"
