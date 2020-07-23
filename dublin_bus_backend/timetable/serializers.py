from rest_framework import serializers
from timetable.models import timetable


class timetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = timetable
        fields = '__all__'
