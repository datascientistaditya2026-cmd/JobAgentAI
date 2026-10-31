from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    full_name = models.CharField(
        max_length=200,
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    location = models.CharField(
        max_length=200,
        blank=True
    )

    preferred_roles = models.TextField(
        blank=True,
        help_text="Example: Python Developer, AI Engineer, Data Scientist"
    )

    preferred_locations = models.TextField(
        blank=True,
        help_text="Example: Bangalore, Chennai, Remote"
    )

    skills = models.TextField(
        blank=True,
        help_text="Example: Python, Django, SQL, Machine Learning"
    )

    education = models.TextField(
        blank=True
    )

    experience = models.TextField(
        blank=True
    )

    expected_salary = models.CharField(
        max_length=100,
        blank=True
    )

    remote_preference = models.CharField(
        max_length=50,
        choices=[
            ("remote", "Remote"),
            ("hybrid", "Hybrid"),
            ("onsite", "On-site"),
            ("any", "Any"),
        ],
        default="any"
    )

    bio = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.full_name or self.user.username