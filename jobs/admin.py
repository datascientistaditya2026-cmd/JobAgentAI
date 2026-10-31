from django.contrib import admin

from .models import Job, JobMatch


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):

    list_display = [
        "title",
        "company_name",
        "location",
        "job_type",
        "source",
        "is_active",
        "collected_at",
    ]

    list_filter = [
        "job_type",
        "is_active",
        "source",
    ]

    search_fields = [
        "title",
        "company_name",
        "skills",
        "location",
    ]


@admin.register(JobMatch)
class JobMatchAdmin(admin.ModelAdmin):

    list_display = [
        "user",
        "job",
        "overall_score",
        "skills_score",
        "location_score",
        "created_at",
    ]

    list_filter = [
        "overall_score",
    ]