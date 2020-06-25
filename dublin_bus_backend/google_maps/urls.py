from django.urls import path
from google_maps.views import GoogleMapsAutocomplete, GoogleMapsGetPlaceByID
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('google/get/places', GoogleMapsAutocomplete.as_view()),
    path('google/get/place/coordinates', GoogleMapsGetPlaceByID.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
