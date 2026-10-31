import json

from django.conf import settings
from google import genai


def analyze_application(user, job, resume=None):
    """
    Analyze a candidate against a specific job using Gemini.
    """

    # --------------------------------
    # USER PROFILE
    # --------------------------------

    try:
        profile = user.profile
    except Exception:
        profile = None

    profile_data = {
        "full_name": getattr(profile, "full_name", ""),
        "location": getattr(profile, "location", ""),
        "skills": getattr(profile, "skills", ""),
        "education": getattr(profile, "education", ""),
        "experience": getattr(profile, "experience", ""),
        "preferred_roles": getattr(
            profile,
            "preferred_roles",
            ""
        ),
        "preferred_locations": getattr(
            profile,
            "preferred_locations",
            ""
        ),
        "bio": getattr(profile, "bio", ""),
    }

    # --------------------------------
    # RESUME
    # --------------------------------

    resume_text = ""

    if resume:
        resume_text = resume.extracted_text or ""

    # --------------------------------
    # JOB
    # --------------------------------

    job_data = {
        "title": job.title,
        "company": job.company_name,
        "location": job.location,
        "job_type": job.get_job_type_display(),
        "description": job.description,
        "requirements": job.requirements,
        "skills": job.skills,
    }

    # --------------------------------
    # PROMPT
    # --------------------------------

    prompt = f"""
You are a professional job matching and application analysis assistant.

Analyze how well the candidate matches the job.

IMPORTANT RULES:

1. Use ONLY information provided in the candidate profile
   and resume.

2. Never invent candidate information.

3. Do not assume a skill or experience that is not explicitly
   present in the supplied information.

4. Compare the candidate against the actual job requirements.

5. Be factual and explain the reasoning.

6. Missing skills should only contain skills that are actually
   required by the job but are not present in the candidate
   information.

7. Do not discriminate based on protected characteristics.

8. Return ONLY valid JSON.

Return exactly this structure:

{{
    "overall_score": 0,
    "skills_score": 0,
    "experience_score": 0,
    "education_score": 0,
    "location_score": 0,
    "matching_skills": [],
    "missing_skills": [],
    "strengths": [],
    "concerns": [],
    "explanation": ""
}}

All scores must be numbers between 0 and 100.

--------------------------------
CANDIDATE PROFILE
--------------------------------

{json.dumps(profile_data, indent=2)}

--------------------------------
RESUME
--------------------------------

{resume_text}

--------------------------------
JOB INFORMATION
--------------------------------

{json.dumps(job_data, indent=2)}

--------------------------------
TASK
--------------------------------

Analyze the candidate's fit for this specific job.
"""

    # --------------------------------
    # API KEY
    # --------------------------------

    api_key = getattr(
        settings,
        "GEMINI_API_KEY",
        None
    )

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured."
        )

    # --------------------------------
    # GEMINI
    # --------------------------------

    client = genai.Client(
        api_key=api_key
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    if not response or not response.text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    raw_response = response.text.strip()

    # --------------------------------
    # CLEAN JSON
    # --------------------------------

    if raw_response.startswith("```json"):
        raw_response = raw_response[
            len("```json"):
        ].strip()

    if raw_response.endswith("```"):
        raw_response = raw_response[
            :-3
        ].strip()

    # --------------------------------
    # PARSE
    # --------------------------------

    try:
        result = json.loads(raw_response)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Gemini returned invalid JSON: {e}"
        )

    # --------------------------------
    # VALIDATE
    # --------------------------------

    required_fields = [
        "overall_score",
        "skills_score",
        "experience_score",
        "education_score",
        "location_score",
        "matching_skills",
        "missing_skills",
        "strengths",
        "concerns",
        "explanation",
    ]

    for field in required_fields:

        if field not in result:
            result[field] = (
                [] if field in [
                    "matching_skills",
                    "missing_skills",
                    "strengths",
                    "concerns",
                ]
                else ""
            )

    # --------------------------------
    # NORMALIZE SCORES
    # --------------------------------

    score_fields = [
        "overall_score",
        "skills_score",
        "experience_score",
        "education_score",
        "location_score",
    ]

    for field in score_fields:

        try:
            value = float(result[field])

        except (TypeError, ValueError):
            value = 0

        value = max(
            0,
            min(100, value)
        )

        result[field] = value

    return result