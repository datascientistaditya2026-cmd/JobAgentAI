from django.db import models
from django.contrib.auth.models import User


class Job(models.Model):

    JOB_TYPE_CHOICES = [
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("contract", "Contract"),
        ("internship", "Internship"),
        ("remote", "Remote"),
    ]

    title = models.CharField(max_length=300)

    company_name = models.CharField(max_length=300)

    location = models.CharField(
        max_length=300,
        blank=True
    )

    job_type = models.CharField(
        max_length=50,
        choices=JOB_TYPE_CHOICES,
        default="full_time"
    )

    description = models.TextField()

    requirements = models.TextField(
        blank=True
    )

    skills = models.TextField(
        blank=True
    )

    salary = models.CharField(
        max_length=200,
        blank=True
    )

    source = models.CharField(
        max_length=200
    )

    source_url = models.URLField(
        max_length=1000
    )

    posted_date = models.DateTimeField(
        null=True,
        blank=True
    )

    collected_at = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.title} - {self.company_name}"


class JobMatch(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="job_matches"
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="matches"
    )

    overall_score = models.FloatField(
        default=0
    )

    skills_score = models.FloatField(
        default=0
    )

    education_score = models.FloatField(
        default=0
    )

    experience_score = models.FloatField(
        default=0
    )

    location_score = models.FloatField(
        default=0
    )

    explanation = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "job"],
                name="unique_user_job_match"
            )
        ]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.job.title} - "
            f"{self.overall_score}%"
        )