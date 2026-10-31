import re


def _slug(value):
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return value.strip("-")


def build_naukri_search_url(preferred_roles, preferred_locations):
    role = (preferred_roles or "jobs").split(",")[0]
    location = (preferred_locations or "india").split(",")[0]

    return (
        "https://www.naukri.com/"
        f"{_slug(role)}-jobs-in-{_slug(location)}"
    )