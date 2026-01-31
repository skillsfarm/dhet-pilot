from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import CuidModel


class Occupation(CuidModel):
    """
    OFO (Organising Framework for Occupations) occupation data.
    Managed by content managers and admins.
    """

    ofo_code = models.CharField(max_length=20, unique=True)
    ofo_title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(
        default=0, help_text="Typical years of experience required"
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Occupation"
        verbose_name_plural = "Occupations"
        ordering = ["ofo_code"]

    def __str__(self):
        return f"{self.ofo_code} - {self.ofo_title}"


class Skill(CuidModel):
    """
    Skills that can be associated with occupation tasks.
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"
        ordering = ["name"]

    def __str__(self):
        return self.name


class OccupationTask(CuidModel):
    """
    Tasks associated with an occupation.
    Used to generate assessments for candidates.
    """

    occupation = models.ForeignKey(
        Occupation, on_delete=models.CASCADE, related_name="tasks"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill, related_name="tasks", blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Occupation Task"
        verbose_name_plural = "Occupation Tasks"
        ordering = ["occupation", "title"]

    def __str__(self):
        return f"{self.occupation.ofo_code} - {self.title}"
