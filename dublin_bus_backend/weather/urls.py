from django.urls import path
from weather.views import GetWeather
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('arrival/weather', GetWeather.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
