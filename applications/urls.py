from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.application_list,
        name="application_list"
    ),

    path(
        "create/<int:job_id>/",
        views.application_create,
        name="application_create"
    ),

    path(
        "<int:application_id>/",
        views.application_detail,
        name="application_detail"
    ),

    path(
        "<int:application_id>/generate-cover-letter/",
        views.generate_cover_letter_view,
        name="generate_cover_letter"
    ),

    path(
        "<int:application_id>/analyze/",
        views.analyze_application_view,
        name="analyze_application"
    ),
]