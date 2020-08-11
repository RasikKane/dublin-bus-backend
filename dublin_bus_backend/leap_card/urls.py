from django.urls import path
from leap_card.views import LeapCardGetUserInfo
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('leapcard/get/cardinfo', LeapCardGetUserInfo.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
