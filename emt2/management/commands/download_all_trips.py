from django.core.management.base import BaseCommand

from emt2.client import Conductor
from emt2.models import BusLine


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Downloading trips..."))

        conductor = Conductor()
        for bus_line in BusLine.objects.all():
            conductor.get_trip_for_line(bus_line.id)

        self.stdout.write(self.style.SUCCESS(f"Successfully synced trips."))
