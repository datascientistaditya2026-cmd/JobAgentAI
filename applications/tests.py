from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from jobs.models import Job

from .models import Application


class ApplicationFlowTests(TestCase):

	def setUp(self):
		self.user = User.objects.create_user(
			username="candidate",
			password="test-password",
		)
		self.job = Job.objects.create(
			title="Python Developer",
			company_name="Example",
			description="Build Python services.",
			source="Greenhouse",
			source_url="https://example.com/jobs/python-developer",
		)
		self.application = Application.objects.create(
			user=self.user,
			job=self.job,
		)
		self.client.force_login(self.user)

	def test_saving_applied_status_sets_applied_at(self):
		response = self.client.post(
			reverse(
				"application_detail",
				args=[self.application.id],
			),
			{
				"action": "save",
				"status": "applied",
				"application_mode": "manual",
				"cover_letter": "Ready to submit.",
			},
		)

		self.assertRedirects(
			response,
			reverse(
				"application_detail",
				args=[self.application.id],
			),
		)
		self.application.refresh_from_db()
		self.assertIsNotNone(self.application.applied_at)

	def test_duplicate_application_is_rejected_by_database_constraint(self):
		with self.assertRaises(IntegrityError):
			Application.objects.create(
				user=self.user,
				job=self.job,
			)
