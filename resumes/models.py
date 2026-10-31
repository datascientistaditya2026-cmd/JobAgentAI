from django.db import models
from django.contrib.auth.models import User


class Resume(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="resumes"
    )

    title = models.CharField(
        max_length=200
    )

    file = models.FileField(
        upload_to="resumes/"
    )

    extracted_text = models.TextField(
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    is_primary = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.title