from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class SignupForm(forms.Form):

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter username"
            }
        )
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter email"
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter password"
            }
        )
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm password"
            }
        )
    )

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Username already exists."
            )

        return username

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data


class ProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile

        fields = [
            "full_name",
            "phone",
            "location",
            "preferred_roles",
            "preferred_locations",
            "skills",
            "education",
            "experience",
            "expected_salary",
            "remote_preference",
            "bio",
        ]

        widgets = {

            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your full name"
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Phone number"
                }
            ),

            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Current location"
                }
            ),

            "preferred_roles": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Python Developer, AI Engineer..."
                }
            ),

            "preferred_locations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Bangalore, Chennai, Remote..."
                }
            ),

            "skills": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Python, Django, SQL..."
                }
            ),

            "education": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "MBA, B.Tech, etc."
                }
            ),

            "experience": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Describe your experience"
                }
            ),

            "expected_salary": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: 6 LPA"
                }
            ),

            "remote_preference": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Tell us about yourself..."
                }
            ),
        }