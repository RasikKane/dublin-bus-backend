from rest_framework import serializers
from bus_stops.models import BusStops


class BusStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusStops
        fields = ['stop_id', 'stop_name', 'stop_lat', 'stop_lng']
