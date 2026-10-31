from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import UserProfile
from .forms import ProfileForm


@login_required
def profile_view(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "full_name": request.user.username
        }
    )

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully."
            )

            return redirect("profile")

    else:

        form = ProfileForm(
            instance=profile
        )

    return render(
        request,
        "profile/profile.html",
        {
            "form": form,
            "profile": profile
        }
    )