from django.core.management.base import BaseCommand

from emt2.client import Conductor


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Downloading bus lines..."))

        conductor = Conductor()
        conductor.get_all_lines()

        self.stdout.write(self.style.SUCCESS(f"Successfully synced bus lines."))
