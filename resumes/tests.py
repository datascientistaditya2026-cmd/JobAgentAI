from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .forms import ResumeForm


class ResumeFormTests(TestCase):

	def test_only_pdf_files_are_accepted(self):
		uploaded_file = SimpleUploadedFile(
			"resume.docx",
			b"not a pdf",
			content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
		)

		form = ResumeForm(
			data={"title": "Resume"},
			files={"file": uploaded_file},
		)

		self.assertFalse(form.is_valid())
		self.assertIn("Only PDF resumes are supported.", form.errors["file"])

	def test_pdf_files_under_size_limit_are_accepted(self):
		uploaded_file = SimpleUploadedFile(
			"resume.pdf",
			b"%PDF-1.4 test",
			content_type="application/pdf",
		)

		form = ResumeForm(
			data={"title": "Resume"},
			files={"file": uploaded_file},
		)

		self.assertTrue(form.is_valid(), form.errors)
