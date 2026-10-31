from django.urls import path
from . import views


urlpatterns = [
    path(
        "discover/",
        views.discover_jobs_view,
        name="discover_jobs"
    ),
]