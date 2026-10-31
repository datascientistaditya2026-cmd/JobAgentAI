from jobs.models import Job
from agents.job_sources import JobData


def save_job(job_data: JobData):
    """
    Save a discovered job into the database.

    Existing jobs are identified primarily by source URL.
    """

    if not job_data.source_url:
        return None, False

    job, created = Job.objects.update_or_create(
        source_url=job_data.source_url,
        defaults={
            "title": job_data.title,
            "company_name": job_data.company_name,
            "location": job_data.location,
            "job_type": job_data.job_type,
            "description": job_data.description,
            "requirements": job_data.requirements,
            "skills": job_data.skills,
            "salary": job_data.salary,
            "source": job_data.source,
            "posted_date": job_data.posted_date,
            "is_active": True,
        },
    )

    return job, created


def save_jobs(job_data_list):
    """
    Save multiple discovered jobs.
    """

    created_count = 0
    updated_count = 0

    for job_data in job_data_list:

        job, created = save_job(job_data)

        if job is None:
            continue

        if created:
            created_count += 1
        else:
            updated_count += 1

    return {
        "created": created_count,
        "updated": updated_count,
        "total": created_count + updated_count,
    }