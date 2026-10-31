from django import forms
from .models import Resume


class ResumeForm(forms.ModelForm):

    MAX_FILE_SIZE = 5 * 1024 * 1024

    class Meta:
        model = Resume

        fields = [
            "title",
            "file",
            "is_primary",
        ]

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: AI ML Engineer Resume"
                }
            ),

            "file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf"
                }
            ),

            "is_primary": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        filename = uploaded_file.name.lower()

        if not filename.endswith(".pdf"):
            raise forms.ValidationError(
                "Only PDF resumes are supported."
            )

        if uploaded_file.size > self.MAX_FILE_SIZE:
            raise forms.ValidationError(
                "Resume file must be 5 MB or smaller."
            )

        if uploaded_file.content_type not in {
            "application/pdf",
            "application/octet-stream",
        }:
            raise forms.ValidationError(
                "The uploaded file must be a PDF."
            )

        return uploaded_file