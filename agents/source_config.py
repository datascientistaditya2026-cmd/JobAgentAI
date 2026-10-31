import json
import os


DEFAULT_GREENHOUSE_COMPANIES = [
    {
        "name": "Stripe",
        "board_token": "stripe",
    },
    {
        "name": "GitLab",
        "board_token": "gitlab",
    },
    {
        "name": "Coinbase",
        "board_token": "coinbase",
    },
]


def _load_greenhouse_companies():
    raw_config = os.getenv("GREENHOUSE_COMPANIES_JSON")

    if raw_config is None:
        return DEFAULT_GREENHOUSE_COMPANIES

    try:
        companies = json.loads(raw_config)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "GREENHOUSE_COMPANIES_JSON must contain valid JSON."
        ) from exc

    if not isinstance(companies, list):
        raise ValueError(
            "GREENHOUSE_COMPANIES_JSON must be a JSON list."
        )

    valid_companies = []

    for company in companies:
        if not isinstance(company, dict):
            continue

        name = str(company.get("name", "")).strip()
        board_token = str(company.get("board_token", "")).strip()

        if name and board_token:
            valid_companies.append(
                {
                    "name": name,
                    "board_token": board_token,
                }
            )

    return valid_companies


GREENHOUSE_COMPANIES = _load_greenhouse_companies()