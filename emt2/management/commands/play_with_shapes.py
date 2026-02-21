from django.core.management.base import BaseCommand

from emt2.models import BusLine, BusStop


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
        bus_stop: BusStop = BusStop.objects.get(id=65)

        trip = bus_stop.trips.filter(bus_line__id=20)
        print("TRips for 20 on 557> ", trip)
        ## TODO -if it has multiple trips is head or tail put them togeter.
        ## TODO - append the other part of the shape nad get 1/3 of total
        shape = trip[0].shapes.first()
        shape_2 = trip[1].shapes.first()
        print(shape, shape_2, "<shapes")

        # The path the bus takes
        ordered_shape = shape.get_shape_as_json()
        ordered_shape_2 = shape_2.get_shape_as_json()
        ordered_shape_2 = ordered_shape_2[(len(ordered_shape_2) // 2) :]

        print(len(ordered_shape), len(ordered_shape_2), "<len of shapes")

        # Stop lat lon
        stop_location = {"lat": str(bus_stop.lat), "lon": str(bus_stop.lon)}

        print(stop_location)
        print(len(ordered_shape))
        where_stop_is = self.find_closest_index(ordered_shape, stop_location)
        print(where_stop_is)
        route_to_stop = (
            ordered_shape_2 + ordered_shape[: where_stop_is + 2]
        )  ## Removing the ahead stops
        print(route_to_stop, bus_stop.name)
        # Looks nice https://codepen.io/ciurana2016/pen/KwMOrWr?editors=1000
