from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from agents.cover_letter_agent import generate_cover_letter
from agents.application_analysis_agent import analyze_application
from applications.models import Application
from jobs.models import Job, JobMatch
from resumes.models import Resume


@login_required
def application_create(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id,
        is_active=True
    )

    existing_application = Application.objects.filter(
        user=request.user,
        job=job
    ).first()

    if existing_application:
        messages.info(
            request,
            "You already have an application for this job."
        )

        return redirect(
            "application_detail",
            application_id=existing_application.id
        )

    resumes = Resume.objects.filter(
        user=request.user
    ).order_by(
        "-is_primary",
        "-uploaded_at"
    )

    if request.method == "POST":

        resume_id = request.POST.get("resume")

        resume = None

        if resume_id:
            resume = get_object_or_404(
                Resume,
                id=resume_id,
                user=request.user
            )

        # Get existing AI match score
        job_match = JobMatch.objects.filter(
            user=request.user,
            job=job
        ).first()

        match_score = (
            job_match.overall_score
            if job_match
            else 0
        )

        application = Application.objects.create(
            user=request.user,
            job=job,
            resume=resume,
            match_score=match_score,
            status="review",
            application_mode="manual",
        )

        messages.success(
            request,
            "Application created and moved to review."
        )

        return redirect(
            "application_detail",
            application_id=application.id
        )

    return render(
        request,
        "applications/application_create.html",
        {
            "job": job,
            "resumes": resumes,
        }
    )


@login_required
def application_detail(request, application_id):

    application = get_object_or_404(
        Application.objects.select_related(
            "job",
            "resume"
        ),
        id=application_id,
        user=request.user
    )

    if request.method == "POST":

        action = request.POST.get("action")

        # --------------------------------
        # SAVE APPLICATION DETAILS
        # --------------------------------
        if action == "save":

            cover_letter = request.POST.get(
                "cover_letter",
                ""
            ).strip()

            status = request.POST.get(
                "status",
                application.status
            )

            application_mode = request.POST.get(
                "application_mode",
                application.application_mode
            )

            valid_statuses = dict(
                Application.STATUS_CHOICES
            )

            valid_modes = dict(
                Application.MODE_CHOICES
            )

            if status in valid_statuses:
                application.status = status

            if application_mode in valid_modes:
                application.application_mode = application_mode

            application.cover_letter = cover_letter

            if application.status == "applied":
                application.applied_at = application.applied_at or timezone.now()
            else:
                application.applied_at = None

            application.save()

            messages.success(
                request,
                "Application details saved successfully."
            )

            return redirect(
                "application_detail",
                application_id=application.id
            )

        # --------------------------------
        # MARK AS READY
        # --------------------------------
        elif action == "ready":

            application.status = "ready"

            application.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                "Application is now ready to apply."
            )

            return redirect(
                "application_detail",
                application_id=application.id
            )

        # --------------------------------
        # MARK AS APPLIED
        # --------------------------------
        elif action == "applied":

            application.status = "applied"

            application.applied_at = timezone.now()

            application.save(
                update_fields=[
                    "status",
                    "applied_at",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                "Application marked as applied."
            )

            return redirect(
                "application_detail",
                application_id=application.id
            )

    return render(
        request,
        "applications/application_detail.html",
        {
            "application": application,
            "status_choices": Application.STATUS_CHOICES,
            "mode_choices": Application.MODE_CHOICES,
        }
    )


@login_required
def application_list(request):

    applications = Application.objects.filter(
        user=request.user
    ).select_related(
        "job",
        "resume"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "applications/application_list.html",
        {
            "applications": applications,
        }
    )

@login_required
def generate_cover_letter_view(request, application_id):

    application = get_object_or_404(
        Application.objects.select_related(
            "job",
            "resume"
        ),
        id=application_id,
        user=request.user
    )

    if request.method != "POST":
        return redirect(
            "application_detail",
            application_id=application.id
        )

    try:

        cover_letter = generate_cover_letter(
            user=request.user,
            job=application.job,
            resume=application.resume
        )

        application.cover_letter = cover_letter

        application.save(
            update_fields=[
                "cover_letter",
                "updated_at",
            ]
        )

        messages.success(
            request,
            "AI cover letter generated successfully."
        )

    except Exception as e:

        messages.error(
            request,
            f"Cover letter generation failed: {str(e)}"
        )

    return redirect(
        "application_detail",
        application_id=application.id
    )

@login_required
def analyze_application_view(request, application_id):

    application = get_object_or_404(
        Application.objects.select_related(
            "job",
            "resume"
        ),
        id=application_id,
        user=request.user
    )

    if request.method != "POST":

        return redirect(
            "application_detail",
            application_id=application.id
        )

    try:

        result = analyze_application(
            user=request.user,
            job=application.job,
            resume=application.resume
        )

        # Store the overall score in the application
        application.match_score = result[
            "overall_score"
        ]

        application.save(
            update_fields=[
                "match_score",
                "updated_at",
            ]
        )

        # Store analysis temporarily in session
        request.session[
            f"application_analysis_{application.id}"
        ] = result

        messages.success(
            request,
            "AI application analysis completed successfully."
        )

    except Exception as e:

        messages.error(
            request,
            f"Application analysis failed: {str(e)}"
        )

    return redirect(
        "application_detail",
        application_id=application.id
    )