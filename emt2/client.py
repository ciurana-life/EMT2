from random import choice
from string import ascii_letters, digits

import requests_cache
from django.db import transaction

from .enums import HttpMethod
from .exceptions import APIBadResponseError, APIRequestError
from .models import BusLine, BusStop, Shape, ShapePoint, Trip


class Conductor:
    URL = "https://www.emtpalma.cat"
    HEADERS_TOKEN = {
        "Accept-Language": "en-GB,en;q=0.9",
        "Content-Type": "application/json",
        "Content-Length": "81",
    }
    HEADERS = {
        "Cookie": ";",
    }
    REQUEST_TIMEOUT = (10, 10)
    REQUESTS_CACHE_TIMEOUT = 60 * 10

    def __init__(self) -> None:
        self.session = requests_cache.CachedSession(
            "EMT_CACHE", expire_after=self.REQUESTS_CACHE_TIMEOUT
        )
        self.authorize()

    def post_request(self, path: str, payload: dict, headers: dict) -> dict:
        response = self.session.post(
            url=f"{self.URL}{path}",
            json=payload,
            headers=headers,
            timeout=self.REQUEST_TIMEOUT,
        )
        if response.status_code != 201:
            raise APIRequestError(
                HttpMethod.POST, path, response.status_code, response.text
            )
        return response.json()

    def get_request(self, path: str, headers: dict) -> dict | list:
        response = self.session.get(
            url=f"{self.URL}{path}", headers=headers, timeout=self.REQUEST_TIMEOUT
        )
        if response.status_code != 200:
            raise APIRequestError(
                HttpMethod.POST, path, response.status_code, response.text
            )
        return response.json()

    def authorize(self) -> None:
        token_post_payload = {
            "userTypeId": 1,
            "languageId": 1,
            "deviceTypeId": 1,
            "tokenDevice": "".join([choice(ascii_letters + digits) for _ in range(20)]),
        }
        token_response = self.post_request(
            "/maas/api/v1/user/create-user-anonimous",
            token_post_payload,
            self.HEADERS_TOKEN,
        )
        self.HEADERS["Authorization"] = f"Bearer {token_response["bearerToken"]}"

    def get_all_lines(self) -> list[BusLine]:
        lines_response = self.get_request("/maas/api/v1/agency/lines/", self.HEADERS)

        bus_lines = []

        with transaction.atomic():
            for line in lines_response:
                subline_data = self.get_request(
                    f"/maas/api/v1/agency/lines/{line['id']}/sublines", self.HEADERS
                )
                subline_id = (
                    subline_data[0].get("subLineId") if len(subline_data) > 0 else None
                )

                obj, _ = BusLine.objects.update_or_create(
                    id=line["id"],
                    defaults={
                        "name": line["code"],
                        "az_stops": line["name"],
                        "subline_id": subline_id,
                        "color": f"#{line["routeColor"]}",
                    },
                )
                bus_lines.append(obj)

        return bus_lines

    def get_trip_for_line(self, bus_line_id) -> list[Trip]:
        bus_line = BusLine.objects.get(id=bus_line_id)
        trip_data = self.get_request(
            f"/maas/api/v1/agency/lines/directions-subline?subLineId={bus_line.subline_id}",
            self.HEADERS,
        )
        trips = []
        for trip in trip_data:
            obj, _ = Trip.objects.update_or_create(
                id=trip["tripId"], defaults={"bus_line": bus_line}
            )
            trips.append(obj)
        return trips

    def get_trip_shape(self, bus_line_id) -> list[Shape]:
        """
        Downloads the shapes of a bus line.
        """
        trips = Trip.objects.filter(bus_line_id=bus_line_id)
        shapes = []
        with transaction.atomic():
            for trip in trips:
                shape_data = self.get_request(
                    f"/maas/api/v1/agency/lines/{bus_line_id}/shape?tripId={trip.id}",
                    self.HEADERS,
                )
                shape = Shape.objects.create(trip=trip)
                points = [
                    ShapePoint(
                        shape=shape,
                        order=p["order"],
                        latitude=p["latitude"],
                        longitude=p["longitude"],
                        direction=p.get("direction"),
                    )
                    for p in shape_data
                ]
                ShapePoint.objects.bulk_create(points)
                shapes.append(shape)
        return shapes

    def get_stops(self, bus_line_id) -> list[BusStop]:
        """
        Download all the stops of a bus line and save them in the database.
        """
        trips = Trip.objects.filter(bus_line_id=bus_line_id)
        bus_stops = []

        with transaction.atomic():
            for trip in trips:
                stops_data = self.get_request(
                    f"/maas/api/v1/agency/lines/{bus_line_id}/stops?tripId={trip.id}&isLine=0&isLineNearStop=0&both=1",
                    self.HEADERS,
                )

                for b in stops_data:
                    stop, _ = BusStop.objects.get_or_create(
                        id=b["id"],
                        defaults={
                            "name": b["stopName"],
                            "lat": b["stopLat"],
                            "lon": b["stopLon"],
                        },
                    )

                    stop.trips.add(trip)

                    line_ids = [x["routeId"] for x in b["linesBoth"]]
                    lines_qs = BusLine.objects.filter(id__in=line_ids)
                    stop.bus_lines.add(*lines_qs)

                    bus_stops.append(stop)

        return bus_stops
