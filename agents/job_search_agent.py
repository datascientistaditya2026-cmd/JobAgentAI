from agents.job_sources import (
    get_apify_naukri_jobs,
    get_greenhouse_jobs,
)
from agents.job_collector import save_jobs
from agents.source_config import GREENHOUSE_COMPANIES
from agents.matching_agent import calculate_job_match

from jobs.models import JobMatch


def discover_jobs(
    keyword="",
    location="",
    user=None,
):
    """
    Discover jobs, save them to database,
    and optionally create/update JobMatch for the user.
    """

    if user is not None:

        try:
            profile = user.profile

            if not keyword:
                keyword = profile.preferred_roles or ""

            if not location:
                location = profile.preferred_locations or ""

        except Exception:
            pass

    all_jobs = []
    source_results = []

    if keyword or location:
        try:
            apify_jobs = get_apify_naukri_jobs(
                keyword=keyword,
                location=location,
            )
            all_jobs.extend(apify_jobs)
            source_results.append(
                {
                    "source": "Naukri via Apify",
                    "status": "success",
                    "jobs_found": len(apify_jobs),
                    "jobs_selected": len(apify_jobs),
                }
            )
        except Exception as exc:
            source_results.append(
                {
                    "source": "Naukri via Apify",
                    "status": "failed",
                    "jobs_found": 0,
                    "jobs_selected": 0,
                    "error": str(exc),
                }
            )

    for company in GREENHOUSE_COMPANIES:

        try:

            jobs = get_greenhouse_jobs(
                company_name=company["name"],
                board_token=company["board_token"],
            )

            filtered_jobs = []

            for job in jobs:

                title_text = (
                    job.title or ""
                ).lower()

                searchable_text = " ".join(
                    [
                        title_text,
                        (job.description or "").lower(),
                        (job.skills or "").lower(),
                    ]
                )

                location_text = (
                    job.location or ""
                ).lower()

                # -------------------------
                # Keyword filtering
                # -------------------------

                if keyword:

                    keywords = [
                        item.strip().lower()
                        for item in keyword.split(",")
                        if item.strip()
                    ]

                    keyword_match = any(
                        item in searchable_text
                        for item in keywords
                    )

                    if not keyword_match:
                        continue

                # -------------------------
                # Location filtering
                # -------------------------

                if location:

                    locations = [
                        item.strip().lower()
                        for item in location.split(",")
                        if item.strip()
                    ]

                    location_aliases = {
                        "gurugram": "gurgaon",
                        "gurgaon": "gurugram",
                        "bengaluru": "bangalore",
                        "bangalore": "bengaluru",
                    }

                    location_match = any(
                        item in location_text
                        or location_aliases.get(item, "") in location_text
                        for item in locations
                    )

                    remote_match = (
                        "remote" in location_text
                        and any(
                            "remote" in item
                            for item in locations
                        )
                    )

                    if not location_match and not remote_match:
                        continue

                filtered_jobs.append(job)

            all_jobs.extend(filtered_jobs)

            source_results.append(
                {
                    "source": company["name"],
                    "status": "success",
                    "jobs_found": len(jobs),
                    "jobs_selected": len(filtered_jobs),
                }
            )

        except Exception as e:

            source_results.append(
                {
                    "source": company["name"],
                    "status": "failed",
                    "jobs_found": 0,
                    "jobs_selected": 0,
                    "error": str(e),
                }
            )

    # -------------------------
    # Save jobs
    # -------------------------

    save_result = save_jobs(all_jobs)

    # -------------------------
    # AI Matching
    # -------------------------

    matches_created = 0

    if user is not None:

        try:

            profile = user.profile

            # Get jobs that were just collected
            source_urls = [
                job.source_url
                for job in all_jobs
                if job.source_url
            ]

            saved_jobs = []

            for source_url in source_urls:

                try:

                    from jobs.models import Job

                    job = Job.objects.get(
                        source_url=source_url
                    )

                    saved_jobs.append(job)

                except Job.DoesNotExist:
                    continue

            for job in saved_jobs:

                result = calculate_job_match(
                    profile,
                    job
                )

                JobMatch.objects.update_or_create(
                    user=user,
                    job=job,
                    defaults={
                        "overall_score": result[
                            "overall_score"
                        ],
                        "skills_score": result[
                            "skills_score"
                        ],
                        "education_score": result[
                            "education_score"
                        ],
                        "experience_score": result[
                            "experience_score"
                        ],
                        "location_score": result[
                            "location_score"
                        ],
                        "explanation": result[
                            "explanation"
                        ],
                    },
                )

                matches_created += 1

        except Exception:
            matches_created = 0

    # -------------------------
    # Final result
    # -------------------------

    result = save_result

    result["sources"] = source_results
    result["keyword"] = keyword
    result["location"] = location
    result["matches_created"] = matches_created

    result["source_errors"] = [
        {
            "source": source["source"],
            "error": source["error"],
        }
        for source in source_results
        if source["status"] == "failed"
    ]

    return result