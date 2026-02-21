import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from emt2.models import BusLine, BusStop, Trip


class Command(BaseCommand):

    def find_closest_index(self, ordered_shape, stop_location):
        stop_lat = float(stop_location["lat"])
        stop_lon = float(stop_location["lon"])

        best_idx = -1
        best_dist = float("inf")

        for i, point in enumerate(ordered_shape):
            lat = float(point["latitude"])
            lon = float(point["longitude"])

            # squared distance (no sqrt needed)
            dist = (lat - stop_lat) ** 2 + (lon - stop_lon) ** 2

            if dist < best_dist:
                best_dist = dist
                best_idx = i

        return best_idx

    def handle(self, *args, **options):
        
        self.stdout.write(self.style.NOTICE("[Start] pre-compiling json"))
        all_bus_stops = BusStop.objects.all()
        processed = 0
        of = len(all_bus_stops)

        for bus_stop in all_bus_stops:
            
            self.stdout.write(self.style.NOTICE(f"[Processing] {bus_stop} ({processed} of {of} processed)"))

            bus_stop_object = {"id": bus_stop.id}

            # Get bus lines on that go through that stop (BusLine)
            for bus_line in bus_stop.bus_lines.all():
                # self.stdout.write(self.style.NOTICE(f"\t [#] Processing line {bus_line} "))

                # Get both trips of line
                # The one from stop is for getting the closes point to stop
                # The other one is for appending at the end
                trip_from_stop: Trip = bus_stop.trips.filter(bus_line=bus_line).first()
                try:
                    other_bus_trip: Trip = bus_line.trips.exclude(id=trip_from_stop.id).get()
                except AttributeError:
                    self.stdout.write(self.style.NOTICE(f"\t [#] ERROR on line {bus_line} "))
                    continue

                # Get the shape as json
                shape_stop = trip_from_stop.shapes.first().get_shape_as_json()
                other_shape = other_bus_trip.shapes.first().get_shape_as_json()

                # Get the stop location
                stop_location = {"lat": str(bus_stop.lat), "lon": str(bus_stop.lon)}

                # Find in the shape of the stop where the stop is
                where_stop_is = self.find_closest_index(shape_stop, stop_location)

                # Remove the shape ahead of stop
                route_to_stop = shape_stop[:where_stop_is]

                # If our shape to stop is small (because we are to close to start)
                # We add some part of the other shape
                if len(route_to_stop) < (len(shape_stop) // 2):
                    route_to_stop = other_shape[(len(other_shape) // 3) :] + route_to_stop

                bus_stop_object[bus_line.id] = {
                    "color": bus_line.color,
                    "stop": stop_location,
                    "route": route_to_stop,
                }

            serialized = json.dumps(
                bus_stop_object,
                separators=(",", ":"),
            )

            base_dir = settings.BASE_DIR
            save_path = os.path.join(base_dir, "compiled", f"{bus_stop.id}.json")
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(serialized)
            
            processed += 1
    
        self.stdout.write(self.style.SUCCESS(f"Successfully pre compiled all shapes for all stops."))
