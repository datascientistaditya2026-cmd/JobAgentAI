from django.contrib.auth.models import User
from django.test import TestCase

from jobs.models import Job
from user_profile.models import UserProfile

from .recommendation_agent import generate_job_recommendations
from .matching_agent import calculate_education_score


class MatchingAgentTests(TestCase):

	def test_short_education_tokens_do_not_match_inside_other_words(self):
		score = calculate_education_score(
			"Bachelor of Arts",
			"Experience with database systems required.",
			"",
		)

		self.assertEqual(score, 60)

	def test_recommendations_only_include_india_locations(self):
		user = User.objects.create_user(
			username="india-candidate",
			password="test-password",
		)
		UserProfile.objects.create(
			user=user,
			preferred_locations="India",
			skills="Python",
		)

		india_job = Job.objects.create(
			title="Python Developer India",
			company_name="India Company",
			location="Bengaluru, India",
			description="Python developer role.",
			skills="Python",
			source="Test",
			source_url="https://example.com/india-python",
		)
		Job.objects.create(
			title="Python Developer USA",
			company_name="USA Company",
			location="New York, USA",
			description="Python developer role.",
			skills="Python",
			source="Test",
			source_url="https://example.com/usa-python",
		)

		recommendations = generate_job_recommendations(user)

		self.assertEqual(
			[match.job_id for match in recommendations],
			[india_job.id],
		)
