from django.http import JsonResponse
from rest_framework.views import APIView
from routes_history.serializers import RoutesHistorySerializer
from routes_history.models import RoutesHistory
from rest_framework.response import Response
from rest_framework import status
from bus_stops.models import BusStops
from stops_routes.models import StopsRoutes


# Create your views here.
class LatestUserRoutes(APIView):

    def get(self, request, user_id):

        # Get latest 5 routes
        latest_routes = RoutesHistory.objects.filter(user_id=user_id).order_by('-date_updated')[:5]

        # Create JSON response
        payload = []
        for routes in latest_routes:
            start_bus_stop_data = BusStops.objects.get(pk=routes.start_stop_id)
            dest_bus_stop_data = BusStops.objects.get(pk=routes.dest_stop_id)
            stop_details = {"id": routes.id,
                            "route": routes.route,
                            "direction": routes.direction,
                            "from": start_bus_stop_data.stop_name + " (" + str(routes.start_stop_id) + ")",
                            "to": dest_bus_stop_data.stop_name + " (" + str(routes.dest_stop_id) + ")"}
            payload.append(stop_details)

        # Return response
        return JsonResponse(payload, safe=False)

    def post(self, request):
        try:
            # Check if route exists
            old_route = RoutesHistory.objects.get(start_stop_id=request.data.get('start_stop_id'),
                                                  dest_stop_id=request.data.get('dest_stop_id'),
                                                  user_id=request.data.get('user_id'))

            # Update route
            serializer = RoutesHistorySerializer(old_route, data=request.data)
        except RoutesHistory.DoesNotExist:
            # Create route
            serializer = RoutesHistorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LatestWaypointsBetweenUserRoutes(APIView):

    def get(self, request, id):

        # Get history
        route = RoutesHistory.objects.get(id=id)

        # Checking the small/large prog no
        if route.start_program_number < route.dest_program_number:
            all_stops = StopsRoutes.objects.filter(route=route.route,
                                                   direction=route.direction,
                                                   program_number__range=(route.start_program_number,
                                                                          route.dest_program_number)
                                                   ).order_by('program_number')
        else:
            all_stops = StopsRoutes.objects.filter(route=request.query_params.get('bus_number'),
                                                   direction=request.query_params.get('direction'),
                                                   program_number__range=(route.dest_program_number,
                                                                          route.start_program_number)
                                                   ).order_by('program_number')

        # Create JSON response
        payload = []
        for stops in all_stops:
            stop_details = {'stop_id': stops.stop_id.stop_id, 'stop_name': stops.stop_id.stop_name,
                            'stop_lat': stops.stop_id.stop_lat,
                            'stop_lng': stops.stop_id.stop_lng,
                            'program_number': stops.program_number}
            payload.append(stop_details)

        # Return response
        return JsonResponse(payload, safe=False)
