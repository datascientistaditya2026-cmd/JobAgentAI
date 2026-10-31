from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from agents.job_search_agent import discover_jobs


@login_required
def discover_jobs_view(request):

    if request.method != "POST":
        return redirect("dashboard")

    keyword = request.POST.get(
        "keyword",
        ""
    ).strip()

    location = request.POST.get(
        "location",
        ""
    ).strip()

    try:

        result = discover_jobs(
            keyword=keyword,
            location=location,
            user=request.user,
        )

        created = result.get(
            "created",
            0
        )

        updated = result.get(
            "updated",
            0
        )

        total = result.get(
            "total",
            0
        )

        matches_created = result.get(
            "matches_created",
            0
        )

        source_errors = result.get("source_errors", [])

        for source_error in source_errors:
            messages.warning(
                request,
                f"{source_error['source']}: {source_error['error']}",
            )

        messages.success(
            request,
            (
                f"Job search completed. "
                f"{total} jobs processed, "
                f"{created} new jobs added, "
                f"{updated} jobs updated, "
                f"{matches_created} matches generated."
            )
        )

    except Exception as e:

        messages.error(
            request,
            f"Job search failed: {str(e)}"
        )

    return redirect("dashboard")