from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.job_list,
        name="job_list"
    ),

    path(
        "recommended/",
        views.recommended_jobs,
        name="recommended_jobs"
    ),

    path(
        "<int:job_id>/",
        views.job_detail,
        name="job_detail"
    ),

    path(
        "<int:job_id>/analyze/",
        views.analyze_job_match,
        name="analyze_job_match"
    ),
]