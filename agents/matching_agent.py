import re


def normalize_text(text):
    """
    Convert text into a normalized lowercase string.
    """
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_items(text):
    """
    Convert comma/newline/semicolon separated text into a set.
    """
    if not text:
        return set()

    text = text.replace("\n", ",")
    text = text.replace(";", ",")

    items = []

    for item in text.split(","):
        item = normalize_text(item).strip()

        if item:
            items.append(item)

    return set(items)


def calculate_skills_score(user_skills, job_skills, job_requirements=""):
    """
    Calculate skill similarity between user and job.
    """

    user_skill_set = extract_items(user_skills)
    job_skill_set = extract_items(job_skills)

    # If skills field is empty, try requirements
    if not job_skill_set:
        job_skill_set = extract_items(job_requirements)

    if not job_skill_set:
        return 0, []

    matched_skills = []

    for job_skill in job_skill_set:

        for user_skill in user_skill_set:

            if (
                job_skill == user_skill
                or job_skill in user_skill
                or user_skill in job_skill
            ):
                matched_skills.append(job_skill)
                break

    matched_skills = list(set(matched_skills))

    score = (len(matched_skills) / len(job_skill_set)) * 100

    return round(score, 2), matched_skills


def calculate_location_score(user_location, preferred_locations, job_location):
    """
    Calculate location compatibility.
    """

    user_location = normalize_text(user_location)
    preferred_locations = normalize_text(preferred_locations)
    job_location = normalize_text(job_location)

    if not job_location:
        return 50

    # Remote job
    if "remote" in job_location:
        return 100

    # Any location preference
    if "any" in preferred_locations:
        return 100

    preferred_list = extract_items(preferred_locations)

    for location in preferred_list:

        if location in job_location:
            return 100

    if user_location and user_location in job_location:
        return 100

    return 30


def calculate_education_score(user_education, job_description, job_requirements):
    """
    Basic education matching.
    """

    education = normalize_text(user_education)
    job_text = normalize_text(
        f"{job_description} {job_requirements}"
    )

    if not education:
        return 50

    education_keywords = [
        "btech",
        "b.e",
        "be",
        "bachelor",
        "mtech",
        "m.e",
        "me",
        "master",
        "mba",
        "bca",
        "mca",
        "phd",
        "degree",
    ]

    user_keywords = [
        keyword
        for keyword in education_keywords
        if re.search(rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])", education)
    ]

    if not user_keywords:
        return 50

    matched = [
        keyword
        for keyword in user_keywords
        if re.search(rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])", job_text)
    ]

    if matched:
        return 100

    return 60


def calculate_experience_score(user_experience, job_description, job_requirements):
    """
    Basic experience matching.

    This is intentionally conservative because resume text may not
    contain a perfectly structured experience value.
    """

    user_text = normalize_text(user_experience)

    job_text = normalize_text(
        f"{job_description} {job_requirements}"
    )

    # Fresher / entry-level job
    fresher_keywords = [
        "fresher",
        "freshers",
        "entry level",
        "0 years",
        "no experience",
        "graduate",
    ]

    if any(keyword in job_text for keyword in fresher_keywords):
        return 100

    # Try to find required years
    matches = re.findall(
        r"(\d+)\s*\+?\s*(?:years?|yrs?)",
        job_text
    )

    if not matches:
        return 70

    required_years = int(matches[0])

    # Try to find user's years
    user_matches = re.findall(
        r"(\d+)\s*\+?\s*(?:years?|yrs?)",
        user_text
    )

    if user_matches:
        user_years = int(user_matches[0])
    else:
        # If experience exists but years are not specified
        user_years = 0

    if user_years >= required_years:
        return 100

    if required_years == 0:
        return 100

    score = (user_years / required_years) * 100

    return round(min(score, 100), 2)


def generate_explanation(
    skills_score,
    education_score,
    experience_score,
    location_score,
    matched_skills,
):
    """
    Generate a human-readable explanation.
    """

    explanation_parts = []

    if matched_skills:
        explanation_parts.append(
            "Matching skills: "
            + ", ".join(sorted(matched_skills))
            + "."
        )
    else:
        explanation_parts.append(
            "No strong skill overlap was detected."
        )

    if skills_score >= 80:
        explanation_parts.append(
            "The candidate has a strong skills match."
        )
    elif skills_score >= 50:
        explanation_parts.append(
            "The candidate has a moderate skills match."
        )
    else:
        explanation_parts.append(
            "There is a significant skills gap."
        )

    if education_score >= 80:
        explanation_parts.append(
            "Education appears compatible with the job."
        )
    else:
        explanation_parts.append(
            "Education compatibility is uncertain or partial."
        )

    if experience_score >= 80:
        explanation_parts.append(
            "Experience requirements appear suitable."
        )
    elif experience_score >= 50:
        explanation_parts.append(
            "Experience compatibility is partial."
        )
    else:
        explanation_parts.append(
            "The required experience may be a major gap."
        )

    if location_score >= 80:
        explanation_parts.append(
            "Location preference is compatible."
        )
    else:
        explanation_parts.append(
            "Location preference may be a concern."
        )

    return " ".join(explanation_parts)


def calculate_job_match(user_profile, job):
    """
    Main matching agent.

    Returns:
        overall_score
        individual scores
        explanation
    """

    skills_score, matched_skills = calculate_skills_score(
        user_profile.skills,
        job.skills,
        job.requirements,
    )

    location_score = calculate_location_score(
        user_profile.location,
        user_profile.preferred_locations,
        job.location,
    )

    education_score = calculate_education_score(
        user_profile.education,
        job.description,
        job.requirements,
    )

    experience_score = calculate_experience_score(
        user_profile.experience,
        job.description,
        job.requirements,
    )

    # Weighted score
    overall_score = (
        skills_score * 0.45
        + experience_score * 0.25
        + education_score * 0.15
        + location_score * 0.15
    )

    overall_score = round(overall_score, 2)

    explanation = generate_explanation(
        skills_score,
        education_score,
        experience_score,
        location_score,
        matched_skills,
    )

    return {
        "overall_score": overall_score,
        "skills_score": skills_score,
        "education_score": education_score,
        "experience_score": experience_score,
        "location_score": location_score,
        "matched_skills": matched_skills,
        "explanation": explanation,
    }