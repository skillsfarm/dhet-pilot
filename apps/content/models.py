from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import CuidModel


class Industry(CuidModel):
    """
    Industry lookup model.
    """

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Industry"
        verbose_name_plural = "Industries"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Occupation(CuidModel):
    """
    OFO (Organising Framework for Occupations) occupation data.
    Managed by content managers and admins.
    """

    ofo_code = models.CharField(max_length=20, unique=True)
    ofo_title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    industry = models.ForeignKey(
        Industry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="occupations",
    )
    years_of_experience = models.PositiveIntegerField(
        default=0, help_text="Typical years of experience required"
    )
    preferred_nqf_level = models.PositiveIntegerField(
        default=0,
        help_text="Preferred NQF level (0=Any, 4=Matric, 5=Certificate, 6=Diploma, 7=Degree, 8=Honours, 9=Masters, 10=Doctorate)",
    )
    # Optional file attachments
    files = models.ManyToManyField(
        "storage.File",
        blank=True,
        related_name="occupations",
        help_text="Optional files attached to this occupation",
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


class OccupationMedia(CuidModel):
    """
    Multimedia content for occupations (videos, PDFs, images).
    Can be from remote sources (YouTube, Vimeo) or local storage.
    """

    class MediaType(models.TextChoices):
        VIDEO = "video", "Video"
        PDF = "pdf", "PDF Document"
        IMAGE = "image", "Image"
        AUDIO = "audio", "Audio"
        LINK = "link", "External Link"

    class SourceType(models.TextChoices):
        REMOTE = "remote", "Remote URL (YouTube, Vimeo, etc.)"
        LOCAL = "local", "Local File Storage"

    occupation = models.ForeignKey(
        Occupation, on_delete=models.CASCADE, related_name="media_items"
    )
    is_global = models.BooleanField(
        default=False, help_text="Visible to all candidates in the content feed"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    media_type = models.CharField(max_length=20, choices=MediaType.choices)
    source_type = models.CharField(
        max_length=20, choices=SourceType.choices, default=SourceType.REMOTE
    )

    remote_url = models.URLField(
        blank=True, help_text="URL for remote media (YouTube, Vimeo, etc.)"
    )
    embed_code = models.TextField(
        blank=True, help_text="Optional embed HTML code for remote media"
    )
    local_file = models.ForeignKey(
        "storage.File",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="occupation_media",
        help_text="Local file from storage",
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    is_featured = models.BooleanField(default=False, help_text="Show as featured media")
    is_active = models.BooleanField(
        default=True, help_text="Media is visible to candidates"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Occupation Media"
        verbose_name_plural = "Occupation Media"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.occupation.ofo_code} - {self.title}"

    def get_url(self):
        if self.source_type == self.SourceType.REMOTE:
            return self.remote_url
        if self.source_type == self.SourceType.LOCAL and self.local_file:
            return self.local_file.file.url
        return ""

    def get_embed_html(self):
        """Return raw embed HTML or empty string."""
        return self.embed_code or ""

    def get_display_url(self):
        return self.get_url()

    @property
    def is_video(self):
        return self.media_type == self.MediaType.VIDEO

    @property
    def is_pdf(self):
        return self.media_type == self.MediaType.PDF

    @property
    def is_image(self):
        return self.media_type == self.MediaType.IMAGE
