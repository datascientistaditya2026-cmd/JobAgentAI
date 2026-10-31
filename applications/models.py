from django.db import models
from django.contrib.auth.models import User
from jobs.models import Job
from resumes.models import Resume


class Application(models.Model):

    STATUS_CHOICES = [
        ("saved", "Saved"),
        ("review", "Review"),
        ("ready", "Ready to Apply"),
        ("applied", "Applied"),
        ("interview", "Interview"),
        ("rejected", "Rejected"),
        ("selected", "Selected"),
    ]

    MODE_CHOICES = [
        ("manual", "Manual"),
        ("assisted", "Assisted"),
        ("automatic", "Automatic"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    resume = models.ForeignKey(
        Resume,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    match_score = models.FloatField(
        default=0
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="saved"
    )

    application_mode = models.CharField(
        max_length=30,
        choices=MODE_CHOICES,
        default="manual"
    )

    cover_letter = models.TextField(
        blank=True
    )

    applied_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "job"],
                name="unique_user_job_application",
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"