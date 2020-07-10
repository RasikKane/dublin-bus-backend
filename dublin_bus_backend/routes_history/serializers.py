from rest_framework import serializers
from routes_history.models import RoutesHistory


class RoutesHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutesHistory
        fields = '__all__'
