from .models import Job, JobMatch
from agents.matching_agent import calculate_job_match


def search_jobs(keyword="", location="", job_type=""):
    jobs = Job.objects.filter(is_active=True)

    if keyword:
        jobs = jobs.filter(title__icontains=keyword)

    if location:
        jobs = jobs.filter(location__icontains=location)

    if job_type:
        jobs = jobs.filter(job_type=job_type)

    return jobs.order_by("-posted_date", "-collected_at")


def create_job_match(user, job):
    """
    Calculate and save/update a user's match for a job.
    """

    user_profile = user.profile

    result = calculate_job_match(
        user_profile,
        job,
    )

    job_match, created = JobMatch.objects.update_or_create(
        user=user,
        job=job,
        defaults={
            "overall_score": result["overall_score"],
            "skills_score": result["skills_score"],
            "education_score": result["education_score"],
            "experience_score": result["experience_score"],
            "location_score": result["location_score"],
            "explanation": result["explanation"],
        },
    )

    return job_match, result