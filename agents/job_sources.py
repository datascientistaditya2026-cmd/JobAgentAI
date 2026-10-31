from dataclasses import dataclass
from typing import Optional
import json

import requests
from django.conf import settings

from agents.skill_extractor import extract_skills
from jobs.search_links import build_naukri_search_url


# ============================================================
# JOB DATA
# ============================================================

@dataclass
class JobData:

    title: str

    company_name: str

    location: str = ""

    job_type: str = "full_time"

    description: str = ""

    requirements: str = ""

    skills: str = ""

    salary: str = ""

    source: str = ""

    source_url: str = ""

    posted_date: Optional[object] = None


def _replace_input_values(value, keyword, location, search_url):
    if isinstance(value, str):
        return value.format(
            keyword=keyword,
            location=location,
            search_url=search_url,
        )

    if isinstance(value, list):
        return [
            _replace_input_values(item, keyword, location, search_url)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: _replace_input_values(item, keyword, location, search_url)
            for key, item in value.items()
        }

    return value


def _raise_apify_error(response, action):
    if response.ok:
        return

    if response.status_code == 401 or response.status_code == 403:
        raise ValueError(
            "Apify authorization failed. Rotate the API token and verify "
            "that it can access the configured actor."
        )

    raise ValueError(
        f"Apify {action} failed with HTTP {response.status_code}."
    )


def get_apify_naukri_jobs(keyword, location):
    """Run the configured Apify Naukri actor and normalize its dataset."""
    api_token = getattr(settings, "APIFY_API_TOKEN", None)
    actor_id = getattr(settings, "APIFY_NAUKRI_ACTOR_ID", None)

    if not api_token:
        return []

    search_url = build_naukri_search_url(keyword, location)
    configured_input = getattr(settings, "APIFY_NAUKRI_INPUT_JSON", None)

    if configured_input:
        try:
            actor_input = json.loads(configured_input)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "APIFY_NAUKRI_INPUT_JSON must contain valid JSON."
            ) from exc
        actor_input = _replace_input_values(
            actor_input,
            keyword,
            location,
            search_url,
        )
    else:
        actor_input = {
            "query": (
                "Find current job openings on Naukri.com for these roles: "
                f"{keyword}. Preferred locations: {location}. "
                "Return ONLY a JSON array with objects containing: "
                "title, company_name, location, description, source_url. "
                "Include only jobs matching the requested roles and locations."
            ),
            "modelName": "gpt-4o-mini",
            "debug": False,
        }

    run_response = requests.post(
        f"https://api.apify.com/v2/acts/{actor_id}/runs",
        params={"token": api_token, "waitForFinish": 120},
        json=actor_input,
        headers={"User-Agent": "JobAgentAI/1.0"},
        timeout=150,
    )
    _raise_apify_error(run_response, "actor run")

    run_data = run_response.json().get("data", {})
    run_status = run_data.get("status")

    if run_status not in {"SUCCEEDED", "RUNNING"}:
        raise ValueError(
            f"Apify actor run ended with status {run_status or 'UNKNOWN'}. "
            "Check the actor log."
        )

    dataset_id = run_data.get("defaultDatasetId")

    if not dataset_id:
        return []

    dataset_response = requests.get(
        f"https://api.apify.com/v2/datasets/{dataset_id}/items",
        params={"token": api_token, "clean": "true"},
        headers={"User-Agent": "JobAgentAI/1.0"},
        timeout=30,
    )
    _raise_apify_error(dataset_response, "dataset read")

    raw_items = dataset_response.json()
    items = []

    for item in raw_items:
        if isinstance(item, dict) and item.get("results"):
            result = item["results"]
            if isinstance(result, str):
                result = result.strip()
                if result.startswith("```json"):
                    result = result[7:].strip()
                if result.endswith("```"):
                    result = result[:-3].strip()
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    continue
            if isinstance(result, list):
                items.extend(result)
        elif isinstance(item, dict):
            items.append(item)

    jobs = []

    for item in items:
        title = str(
            item.get("title")
            or item.get("jobTitle")
            or item.get("job_title")
            or ""
        ).strip()
        source_url = str(
            item.get("url")
            or item.get("jobUrl")
            or item.get("job_url")
            or item.get("source_url")
            or item.get("applyUrl")
            or item.get("link")
            or ""
        ).strip()

        if not title or not source_url:
            continue

        description = str(
            item.get("description")
            or item.get("jobDescription")
            or item.get("job_description")
            or ""
        )
        item_location = str(
            item.get("location")
            or item.get("jobLocation")
            or item.get("job_location")
            or location
        ).strip()
        company_name = str(
            item.get("company")
            or item.get("companyName")
            or item.get("company_name")
            or "Naukri Employer"
        ).strip()

        jobs.append(
            JobData(
                title=title,
                company_name=company_name,
                location=item_location,
                description=description,
                requirements=description,
                skills=extract_skills(description),
                source="Naukri via Apify",
                source_url=source_url,
            )
        )

    return jobs


# ============================================================
# GREENHOUSE JOB SOURCE
# ============================================================

def get_greenhouse_jobs(
    company_name,
    board_token
):
    """
    Fetch public jobs from a Greenhouse job board.

    company_name:
        Display name of the company.

    board_token:
        Greenhouse board token.
    """

    url = (
        f"https://boards-api.greenhouse.io/v1/boards/"
        f"{board_token}/jobs?content=true"
    )

    headers = {
        "User-Agent": "JobAgentAI/1.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    jobs = []

    for item in data.get("jobs", []):

        # ----------------------------------------------------
        # Basic information
        # ----------------------------------------------------

        title = item.get(
            "title",
            ""
        ).strip()

        absolute_url = item.get(
            "absolute_url",
            ""
        ).strip()

        # ----------------------------------------------------
        # Location
        # ----------------------------------------------------

        location_data = item.get(
            "location"
        ) or {}

        location = location_data.get(
            "name",
            ""
        ).strip()

        # ----------------------------------------------------
        # Description
        # ----------------------------------------------------

        description = item.get(
            "content",
            ""
        ) or ""

        # ----------------------------------------------------
        # Extract skills
        # ----------------------------------------------------

        skills = extract_skills(
            description
        )

        # ----------------------------------------------------
        # Create JobData
        # ----------------------------------------------------

        job = JobData(

            title=title,

            company_name=company_name,

            location=location,

            job_type="full_time",

            description=description,

            requirements=description,

            skills=skills,

            salary="",

            source="Greenhouse",

            source_url=absolute_url,

            posted_date=None,
        )

        jobs.append(job)

    return jobs