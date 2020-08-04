from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bus_stops.models import BusStops
from stops_routes.models import StopsRoutes
import requests
import math
import logging

# Create a logger for this file
logger = logging.getLogger(__file__)

GOOGLE_MAPS_KEY = "AIzaSyCv4Jkj6OMUVN0swxdIzZMOYu1vaddkooY"


class GoogleMapsAutocomplete(APIView):

    def get(self, request):
        try:
            searched_bus_stops = BusStops.objects.filter(stop_name__icontains=request.query_params.get('query'))

        # Induction of following error handling generates error in autocomplete
        #     if not searched_bus_stops.exists():
        #         raise ObjectDoesNotExist
        # except ObjectDoesNotExist:
        #     logger.exception('exception in google_maps view : BusStops object '
        #                      '- queryset searched_bus_stops is empty')
        #     return Response({"Error: google_maps searched_bus_stops not available"},
        #                     status=status.HTTP_204_NO_CONTENT)
        #     # return Response({"Error: google_maps searched_bus_stops not available"},
        #     # status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('exception in google_maps view BusStops object', e)
            return Response({"Error: google_maps -  BusStops query set"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Get response from Google
        try:
            response = requests.get(url="https://maps.googleapis.com/maps/api/place/autocomplete/json",
                                    params={'input': request.query_params.get('query'),
                                            'key': GOOGLE_MAPS_KEY,
                                            'location': '53.357841,-6.251557', 'radius': 2000}).json()
        except Exception as e:
            logger.exception('exception in google_maps view google maps API response', e)
            return Response({"Error: google_maps -  google map API response "}, status=status.HTTP_400_BAD_REQUEST)

        # Create JSON response
        payload = []

        for searched_bus_stop in searched_bus_stops:

            # Getting all the bus no and direction for stop
            all_bus_numbers = []

            try:
                for bus in StopsRoutes.objects.filter(stop_id=searched_bus_stop.stop_id):
                    all_bus_numbers.append({'direction': bus.direction, 'bus_number': bus.route})
            except Exception as e:
                logger.exception('exception in google_maps view StopsRoutes object', e)
                return Response({"Error: google_maps -  StopsRoutes query set"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            content = {'title': searched_bus_stop.stop_name + " (" + str(searched_bus_stop.stop_id) + ")",
                       'id': searched_bus_stop.stop_id, 'fromDB': True, 'stop_lat': searched_bus_stop.stop_lat,
                       'stop_lng': searched_bus_stop.stop_lng, 'all_bus_numbers': all_bus_numbers}
            payload.append(content)

        for result in response['predictions']:
            content = {'title': result['description'], 'id': result['place_id'], 'fromDB': False}
            payload.append(content)

        try:
            return JsonResponse(payload, safe=False)
        except Exception as e:
            logger.exception('exception in google_maps view while returning JSON response', e)
            return Response({"Error: google_maps - valid JSON response not returned"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleMapsGetPlaceByID(APIView):

    def get(self, request):
        # Get response from Google
        try:
            response = requests.get(url="https://maps.googleapis.com/maps/api/place/details/json",
                                    params={'placeid': request.query_params.get('place_id'),
                                            'key': GOOGLE_MAPS_KEY}).json()
            # Create JSON response
            content = {'lat': response['result']['geometry']['location']['lat'],
                       'lng': response['result']['geometry']['location']['lng']}

        except Exception as e:
            logger.exception('exception in google_maps view google maps API response', e)
            return Response({"Error: google_maps -  google map API response "}, status=status.HTTP_400_BAD_REQUEST)

        try:
            all_bus_stops = BusStops.objects.all()
        except Exception as e:
            logger.exception('exception in google_maps view BusStops object', e)
            return Response({"Error: google_maps -  BusStops query set"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # Create JSON response
            payload = []
            for bus_stop in all_bus_stops:
                if self.calculate_distance(float(content['lat']), float(content['lng']), float(bus_stop.stop_lat),
                                           float(bus_stop.stop_lng)) <= 0.5:
                    # Getting all the bus no and direction for stop
                    all_bus_numbers = []
                    for bus in StopsRoutes.objects.filter(stop_id=bus_stop.stop_id):
                        all_bus_numbers.append({'direction': bus.direction, 'bus_number': bus.route})

                    stop_details = {'stop_id': bus_stop.stop_id, 'stop_name': bus_stop.stop_name,
                                    'stop_lat': bus_stop.stop_lat,
                                    'stop_lng': bus_stop.stop_lng, 'all_bus_numbers': all_bus_numbers}
                    payload.append(stop_details)

        except Exception as e:
            logger.exception('exception in google_maps view while JSON payload generation', e)
            return Response({"Error: google_maps - valid JSON payload not generated"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            return JsonResponse(payload, safe=False)
        except Exception as e:
            logger.exception('exception in timetable view while returning JSON response', e)
            return Response({"Error: timetable - valid JSON response not returned"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Reference: https://stackoverflow.com/questions/51819224/
    # how-to-find-nearest-location-using-latitude-and-longitude-from-a-json-data
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        radlat1 = math.pi * lat1 / 180
        radlat2 = math.pi * lat2 / 180
        theta = lon1 - lon2
        radtheta = math.pi * theta / 180
        dist = math.sin(radlat1) * math.sin(radlat2) + math.cos(radlat1) * math.cos(radlat2) * math.cos(radtheta)
        if dist > 1:
            dist = 1
        dist = math.acos(dist)
        dist = dist * 180 / math.pi
        dist = dist * 60 * 1.1515
        dist = dist * 1.609344
        return dist
