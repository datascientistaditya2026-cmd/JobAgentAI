from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

from user_profile.models import UserProfile
from user_profile.forms import SignupForm


def signup_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            UserProfile.objects.create(
                user=user,
                full_name=username
            )

            login(request, user)

            messages.success(
                request,
                "Account created successfully."
            )

            return redirect("profile")

    else:
        form = SignupForm()

    return render(
        request,
        "accounts/signup.html",
        {"form": form}
    )


def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("dashboard")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "accounts/login.html"
    )


def logout_view(request):

    logout(request)

    return redirect("login")