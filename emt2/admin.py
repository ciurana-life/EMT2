from django.contrib import admin

from .models import BusLine, BusStop, Shape, ShapePoint, Trip

admin.site.register(BusLine)
admin.site.register(Trip)
admin.site.register(Shape)
admin.site.register(ShapePoint)
admin.site.register(BusStop)
