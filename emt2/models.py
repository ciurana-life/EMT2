from django.db import models


class BusLine(models.Model):
    """
    Represents a single bus line.

    Attributes:
        id: Unique numeric identifier used in API calls.
        name: Human-readable line name or code.
        az_stops: Route description (e.g. "First stop - Last stop").
        sub_line_id: Reference to get the TripIds.
        color: hex color.
    """

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    az_stops = models.CharField(max_length=255)
    subline_id = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=6, default="030303")

    def __str__(self):
        return f"{self.name} ({self.az_stops})"


class Trip(models.Model):
    """
    Every line has 2 trips (going "up" and "down")
    """

    id = models.IntegerField(primary_key=True)
    bus_line = models.ForeignKey(
        BusLine, on_delete=models.CASCADE, related_name="trips"
    )

    def __str__(self):
        return f"Trip {self.id} of {self.bus_line.name}"


class BusStop(models.Model):
    """
    Represents a single physical stop location.

    Attributes:
        id: Unique numeric identifier used in API calls. This is also
            the identifier of the physical stop.
        name: Human-readable name of the stop.
        lat: Latitude of the stop in decimal degrees.
        lon: Longitude of the stop in decimal degrees.
        bus_lines: Bus lines that stop there.
        trip_ids: Trip ids related to this stop.
    """

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    lat = models.DecimalField(max_digits=17, decimal_places=14)
    lon = models.DecimalField(max_digits=17, decimal_places=14)

    trips = models.ManyToManyField("Trip", related_name="stops", blank=True)

    bus_lines = models.ManyToManyField("BusLine", related_name="stops", blank=True)

    def __str__(self):
        return f"{self.id} ({self.name})"


class Shape(models.Model):
    """
    Represents the shape (route) of a Trip.
    """

    trip = models.ForeignKey("Trip", on_delete=models.CASCADE, related_name="shapes")

    def __str__(self):
        return f"Shape of Trip {self.trip.id}"

    def get_shape_as_json(self) -> dict:
        # TODO - unmutable
        return [
            {
                "order": point.order,
                "latitude": str(point.latitude),
                "longitude": str(point.longitude),
            }
            for point in self.points.all()
        ]


class ShapePoint(models.Model):
    """
    A geolocated point that belongs to a Shape.
    """

    shape = models.ForeignKey(Shape, on_delete=models.CASCADE, related_name="points")
    order = models.IntegerField()
    latitude = models.DecimalField(max_digits=17, decimal_places=14)
    longitude = models.DecimalField(max_digits=17, decimal_places=14)
    direction = models.CharField(max_length=2)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Shape {self.shape.id} - Point {self.order}"
