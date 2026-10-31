from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import dashboard


urlpatterns = [

    path(
        "",
        dashboard,
        name="dashboard"
    ),

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "accounts/",
        include("accounts.urls")
    ),

    path(
        "profile/",
        include("user_profile.urls")
    ),

    path(
        "resumes/",
        include("resumes.urls")
    ),
    path(
        "jobs/",
        include("jobs.urls")
    ),
    path(
        "agents/",
        include("agents.urls")
    ),
    path(
        "applications/",
        include("applications.urls")
    ),
]


if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )