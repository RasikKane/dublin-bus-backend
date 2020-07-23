from django.urls import path
from timetable.views import PredictArrivalTime
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('arrival/predict', PredictArrivalTime.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
