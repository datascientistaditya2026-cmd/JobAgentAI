from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from jobs.models import Job, JobMatch
from resumes.models import Resume
from applications.models import Application
from user_profile.models import UserProfile
from agents.recommendation_agent import india_job_filter
from jobs.search_links import build_naukri_search_url


@login_required
def dashboard(request):

    # ==========================================
    # USER PROFILE
    # ==========================================

    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    # ==========================================
    # JOB COUNTS
    # ==========================================

    total_jobs = Job.objects.filter(
        is_active=True
    ).count()

    latest_jobs = Job.objects.filter(
        is_active=True
    ).order_by(
        "-posted_date",
        "-collected_at",
    )[:6]

    # ==========================================
    # RECOMMENDED JOBS
    # ==========================================

    recommended_jobs = JobMatch.objects.filter(
        user=request.user,
        job__is_active=True
    ).filter(
        india_job_filter()
    ).select_related(
        "job"
    ).order_by(
        "-overall_score"
    )

    recommended_count = recommended_jobs.count()

    # Top 6 recommendations for dashboard
    top_recommendations = recommended_jobs[:6]

    # ==========================================
    # RESUMES
    # ==========================================

    resumes = Resume.objects.filter(
        user=request.user
    ).order_by(
        "-uploaded_at"
    )

    resume_count = resumes.count()

    # ==========================================
    # APPLICATIONS
    # ==========================================

    applications = Application.objects.filter(
        user=request.user
    ).select_related(
        "job"
    ).order_by(
        "-created_at"
    )

    application_count = applications.count()

    # ==========================================
    # PROFILE COMPLETION
    # ==========================================

    profile_fields = [
        profile.full_name,
        profile.phone,
        profile.location,
        profile.preferred_roles,
        profile.preferred_locations,
        profile.skills,
        profile.education,
        profile.experience,
    ]

    completed_fields = sum(
        1
        for field in profile_fields
        if field
    )

    if profile_fields:

        profile_completion = int(
            (
                completed_fields
                / len(profile_fields)
            ) * 100
        )

    else:

        profile_completion = 0

    # ==========================================
    # CONTEXT
    # ==========================================

    context = {

        "profile": profile,

        "naukri_search_url": build_naukri_search_url(
            profile.preferred_roles,
            profile.preferred_locations,
        ),

        "total_jobs": total_jobs,

        "latest_jobs": latest_jobs,

        "recommended_jobs": recommended_jobs,

        "top_recommendations": top_recommendations,

        "recommended_count": recommended_count,

        "resumes": resumes,

        "resume_count": resume_count,

        "applications": applications,

        "application_count": application_count,

        "profile_completion": profile_completion,
    }

    return render(
        request,
        "dashboard.html",
        context
    )