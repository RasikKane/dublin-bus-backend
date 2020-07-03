from django.urls import path
from stops_routes.views import RoutesPerBusNumber
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('bus/get/routes', RoutesPerBusNumber.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
