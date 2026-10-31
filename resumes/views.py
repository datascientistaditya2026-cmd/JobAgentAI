from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Resume
from .forms import ResumeForm

from .services import (
    extract_text_from_pdf,
    analyze_resume_with_ai,
    update_profile_from_resume
)


@login_required
def resume_list(request):

    resumes = Resume.objects.filter(
        user=request.user
    ).order_by("-uploaded_at")

    return render(
        request,
        "resumes/resume_list.html",
        {
            "resumes": resumes
        }
    )


@login_required
def resume_upload(request):

    if request.method == "POST":

        form = ResumeForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            resume = form.save(
                commit=False
            )

            resume.user = request.user

            resume.save()

            # --------------------------------
            # Extract text from PDF
            # --------------------------------

            if resume.file.name.lower().endswith(".pdf"):

                text = extract_text_from_pdf(
                    resume.file.path
                )

                resume.extracted_text = text

                resume.save(
                    update_fields=["extracted_text"]
                )

                # --------------------------------
                # AI Analysis
                # --------------------------------

                if text:

                    try:

                        data = analyze_resume_with_ai(
                            text
                        )

                        update_profile_from_resume(
                            request.user,
                            data
                        )

                        messages.success(
                            request,
                            "Resume uploaded and profile analyzed successfully."
                        )

                    except Exception as e:

                        print(
                            "AI analysis error:",
                            e
                        )

                        messages.warning(
                            request,
                            "Resume uploaded, but AI analysis failed."
                        )

                else:

                    messages.warning(
                        request,
                        "Resume uploaded, but no text could be extracted."
                    )

            else:

                messages.success(
                    request,
                    "Resume uploaded successfully."
                )

            return redirect(
                "resume_list"
            )

    else:

        form = ResumeForm()

    return render(
        request,
        "resumes/resume_upload.html",
        {
            "form": form
        }
    )