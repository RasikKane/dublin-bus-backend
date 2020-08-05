from django.http import JsonResponse
from django.contrib.admin.utils import flatten
from django.utils import dateparse
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from timetable.models import Timetable
from stops_routes.models import StopsRoutes
from weather.models import Weather
from routes_history.models import RoutesHistory
from bus_stops.models import BusStops
from math import ceil
from numpy import concatenate
import csv
from datetime import datetime
import logging

# Create a logger for this file
logger = logging.getLogger(__file__)


# Create your views here.

class GetWeather(APIView):

    def post(self, request):
        """
        :param request:{'route', 'direction', 'start_stop_id', 'dest_stop_id', 'start_program_number',
        'dest_program_number', 'datetime_input', 'isFromRecentRoutes', 'user_id'};
        return json_response: {'date_weather', 'hour_of_day', 'feels_like', 'wind_speed', 'weather_id',
        'temp', 'temp_min', 'temp_max', 'humidity', 'weather_main','weather_description'}
        """
        # resolve datetime stamp into parameters required for input to  prediction algorithm
        dt_in = dateparse.parse_datetime(str(request.data.get('datetime_input')))
        if not isinstance(dt_in, datetime):
            logger.exception('invalid datetime_input')
            return Response({"Error: date-time is no valid"}, status=status.HTTP_400_BAD_REQUEST)

        # date, hr_date : used for extracting weather parameters for remaining hours from supplies hr_date on given date
        date, hr_date = str(dt_in.date()), dt_in.hour
        sec_date, min_date = dt_in.second, dt_in.minute
        # month, day_of_week, quarter,tArr : features in prediction model input
        month, day_of_week, quarter = dt_in.month, dt_in.weekday(), int(ceil(dt_in.month / 3.))
        tArr = sec_date + min_date * 60 + hr_date * 3600

        # temporary variables for testing
        # month, quarter = 1, 1
        # date = "2018-01-01"

        # Obtain weather data for remaining hours from given hour for fields : [feels_like,wind_speed, weather_id]
        try:
            weather = Weather.objects.get(date_weather=date,
                                          hour_of_day=hr_date
                                          )
        except weather.DoesNotExists:
            logger.exception('exception in weather view : Weather object queryset weather is empty')
            # return Response({"Error: weather not available"}, status=status.HTTP_204_NO_CONTENT)
            return Response({"Error: weather not available"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.exception('exception in weather view Weather object', e)
            return Response({"Error: weather data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Define payload and return prediction weather
        payload = []

        try:
            weather_details = {'date_weather': weather.date_weather,
                               'hour_of_day' : weather.hour_of_day,
                               'feels_like' : weather.feels_like,
                               'wind_speed' : weather.wind_speed,
                               'weather_id' : weather.weather_id,
                               'temp': weather.temp,
                               'temp_min' : weather.temp_min,
                               'temp_max' : weather.temp_max,
                               'humidity' : weather.humidity,
                               'weather_main' : weather.weather_main,
                               'weather_description' : weather.weather_description
                               }
            payload.append(weather_details)
        except Exception as e:
            logger.exception('exception in weather view while JSON payload generation', e)
            return Response({"Error: weather - valid JSON payload not generated"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            return JsonResponse(payload, safe=False)
        except Exception as e:
            logger.exception('exception in weather view while returning JSON response', e)
            return Response({"Error: weather - valid JSON response not returned"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
