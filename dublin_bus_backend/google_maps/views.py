from django.http import JsonResponse
from rest_framework.views import APIView
import requests

GOOGLE_MAPS_KEY = "AIzaSyCv4Jkj6OMUVN0swxdIzZMOYu1vaddkooY"


class GoogleMapsAutocomplete(APIView):

    def get(self, request):
        # Get response from Google
        response = requests.get(url="https://maps.googleapis.com/maps/api/place/autocomplete/json",
                                params={'input': request.query_params.get('query'),
                                        'key': GOOGLE_MAPS_KEY,
                                        'location': '53.357841,-6.251557', 'radius': 2000}).json()
        # Create JSON response
        payload = []
        for result in response['predictions']:
            content = {'title': result['description'], 'id': result['place_id']}
            payload.append(content)

        return JsonResponse(payload, safe=False)


class GoogleMapsGetPlaceByID(APIView):

    def get(self, request):
        # Get response from Google
        response = requests.get(url="https://maps.googleapis.com/maps/api/place/details/json",
                                params={'placeid': request.query_params.get('place_id'), 'key': GOOGLE_MAPS_KEY}).json()
        # Create JSON response
        content = {'lat': response['result']['geometry']['location']['lat'],
                   'lng': response['result']['geometry']['location']['lng']}

        return JsonResponse(content, safe=False)
