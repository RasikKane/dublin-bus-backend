from django.urls import path
from routes_history.views import LatestUserRoutes, LatestWaypointsBetweenUserRoutes
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('routes/save', LatestUserRoutes.as_view()),
    path('routes/getall/latest/<int:user_id>', LatestUserRoutes.as_view()),
    path('routes/getall/waypoints/<int:id>', LatestWaypointsBetweenUserRoutes.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
