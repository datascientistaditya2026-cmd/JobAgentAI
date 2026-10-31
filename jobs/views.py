from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Job
from .services import search_jobs, create_job_match
from .search_links import build_naukri_search_url
from agents.recommendation_agent import generate_job_recommendations


@login_required
def job_list(request):

    keyword = request.GET.get("keyword", "").strip()
    location = request.GET.get("location", "").strip()
    job_type = request.GET.get("job_type", "").strip()

    jobs = search_jobs(
        keyword=keyword,
        location=location,
        job_type=job_type,
    )

    return render(
        request,
        "jobs/job_list.html",
        {
            "jobs": jobs,
            "keyword": keyword,
            "location": location,
            "job_type": job_type,
        },
    )


@login_required
def job_detail(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id,
        is_active=True,
    )

    match = None

    if hasattr(request.user, "job_matches"):
        match = request.user.job_matches.filter(
            job=job
        ).first()

    return render(
        request,
        "jobs/job_detail.html",
        {
            "job": job,
            "match": match,
        },
    )


@login_required
def analyze_job_match(request, job_id):

    if request.method != "POST":
        return redirect("job_detail", job_id=job_id)

    job = get_object_or_404(
        Job,
        id=job_id,
        is_active=True,
    )

    try:

        match, result = create_job_match(
            request.user,
            job,
        )

        messages.success(
            request,
            f"Match analysis completed: "
            f"{result['overall_score']}%",
        )

    except Exception as e:

        messages.error(
            request,
            f"Unable to analyze this job: {str(e)}",
        )

    return redirect(
        "job_detail",
        job_id=job.id,
    )

@login_required
def recommended_jobs(request):

    try:

        recommendations = generate_job_recommendations(
            request.user,
            limit=20
        )

    except Exception as e:

        messages.error(
            request,
            f"Unable to generate recommendations: {str(e)}"
        )

        recommendations = []

    return render(
        request,
        "jobs/recommended_jobs.html",
        {
            "recommendations": recommendations,
            "naukri_search_url": build_naukri_search_url(
                request.user.profile.preferred_roles,
                request.user.profile.preferred_locations,
            ),
        }
    )