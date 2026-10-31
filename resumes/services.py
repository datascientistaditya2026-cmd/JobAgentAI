import json

from pypdf import PdfReader
from user_profile.models import UserProfile
from openai import OpenAI

from django.conf import settings


def extract_text_from_pdf(file_path):

    text = ""

    try:

        reader = PdfReader(file_path)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    except Exception as e:

        print("PDF extraction error:", e)

    return text.strip()


def analyze_resume_with_ai(resume_text):

    client = OpenAI(
        api_key=settings.OPENAI_API_KEY
    )

    prompt = f"""
You are an expert resume analyzer.

Analyze the following resume and return ONLY valid JSON.

Resume:

{resume_text}

Return this structure:

{{
    "full_name": "",
    "phone": "",
    "email": "",
    "location": "",
    "skills": [],
    "education": [],
    "experience": [],
    "projects": [],
    "preferred_roles": [],
    "preferred_locations": [],
    "years_of_experience": 0
}}

Rules:

1. Do not invent information.
2. If information is missing, return an empty string or empty list.
3. Extract skills exactly from the resume.
4. Identify possible job roles based on actual skills and experience.
5. Keep the output valid JSON.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a professional resume analysis AI."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    try:

        return json.loads(content)

    except json.JSONDecodeError:

        print("AI returned invalid JSON")

        return {}


def update_profile_from_resume(user, data):

    profile, created = UserProfile.objects.get_or_create(
        user=user
    )

    if data.get("full_name"):
        profile.full_name = data["full_name"]

    if data.get("phone"):
        profile.phone = data["phone"]

    if data.get("location"):
        profile.location = data["location"]

    if data.get("skills"):
        profile.skills = ", ".join(
            data["skills"]
        )

    if data.get("education"):
        profile.education = "\n".join(
            data["education"]
        )

    if data.get("experience"):
        profile.experience = "\n".join(
            data["experience"]
        )

    if data.get("preferred_roles"):
        profile.preferred_roles = ", ".join(
            data["preferred_roles"]
        )

    if data.get("preferred_locations"):
        profile.preferred_locations = ", ".join(
            data["preferred_locations"]
        )

    profile.save()

    return profile