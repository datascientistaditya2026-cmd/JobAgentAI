from django.db.models import Q

from jobs.models import Job, JobMatch
from agents.matching_agent import calculate_job_match


INDIA_LOCATION_KEYWORDS = (
    "india",
    "bengaluru",
    "bangalore",
    "hyderabad",
    "pune",
    "mumbai",
    "delhi",
    "noida",
    "gurgaon",
    "gurugram",
    "chennai",
    "kolkata",
    "ahmedabad",
)


def india_job_filter(field_prefix="job__"):
    location_filter = Q()

    for keyword in INDIA_LOCATION_KEYWORDS:
        location_filter |= Q(
            **{
                f"{field_prefix}location__icontains": keyword
            }
        )

    return location_filter


def generate_job_recommendations(user, limit=20):
    """
    Analyze active jobs against the user's profile
    and return the highest matching jobs.
    """

    user_profile = user.profile

    jobs = Job.objects.filter(
        is_active=True
    ).filter(
        india_job_filter(field_prefix="")
    )

    recommendations = []

    for job in jobs:

        result = calculate_job_match(
            user_profile,
            job
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
            }
        )

        recommendations.append(job_match)

    recommendations.sort(
        key=lambda match: match.overall_score,
        reverse=True
    )

    return recommendations[:limit]