from django.core.management.base import BaseCommand

from agents.job_search_agent import discover_jobs


class Command(BaseCommand):

    help = "Discover and save jobs from configured sources"

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.WARNING(
                "Starting job discovery..."
            )
        )

        result = discover_jobs()

        self.stdout.write(
            self.style.SUCCESS(
                f"Job discovery completed."
            )
        )

        self.stdout.write(
            f"Created: {result['created']}"
        )

        self.stdout.write(
            f"Updated: {result['updated']}"
        )

        self.stdout.write(
            f"Total: {result['total']}"
        )