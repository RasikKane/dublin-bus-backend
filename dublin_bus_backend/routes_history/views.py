from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from routes_history.serializers import RoutesHistorySerializer
from routes_history.models import RoutesHistory
from bus_stops.models import BusStops
from stops_routes.models import StopsRoutes
import logging

# Create a logger for this file
logger = logging.getLogger(__file__)


# Create your views here.
class LatestUserRoutes(APIView):

    def get(self, request, user_id):

        # Get latest 3 routes
        try:
            latest_routes = RoutesHistory.objects.filter(user_id=user_id).order_by('-date_updated')[:3]

        # Induction of following error handling generates error in autocomplete
        #     if not latest_routes.exists():
        #         raise ObjectDoesNotExist
        # except ObjectDoesNotExist:
        #     logger.exception('exception in routes_history view : stops_routes object queryset latest_routes is empty')
        #     return Response({"Error: Bus record not available"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.exception('exception in route_history view RoutesHistory object', e)
            return Response({"Error: In route_history - query set"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create JSON response
        payload = []

        try:
            for routes in latest_routes:
                start_bus_stop_data = BusStops.objects.get(pk=routes.start_stop_id)
                dest_bus_stop_data = BusStops.objects.get(pk=routes.dest_stop_id)
                stop_details = {"id": routes.id,
                                "route": routes.route,
                                "direction": routes.direction,
                                "from": start_bus_stop_data.stop_name + " (" + str(routes.start_stop_id) + ")",
                                "to": dest_bus_stop_data.stop_name + " (" + str(routes.dest_stop_id) + ")"}
                payload.append(stop_details)
        except Exception as e:
            logger.exception('exception in route_history view while JSON payload generation', e)
            return Response({"Error: In route_history - valid JSON payload not generated"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return response
        try:
            return JsonResponse(payload, safe=False)
        except Exception as e:
            logger.exception('exception in route_history view while returning JSON response', e)
            return Response({"Error: In route_history - valid JSON response not returned"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            # Check if route exists
            # try:
            old_route = RoutesHistory.objects.get(start_stop_id=request.data.get('start_stop_id'),
                                                  dest_stop_id=request.data.get('dest_stop_id'),
                                                  user_id=request.data.get('user_id'),
                                                  route=request.data.get('route'))
            #     if not old_route.DoesNotExist:
            #         raise ObjectDoesNotExist
            # except ObjectDoesNotExist:
            #     logger.exception('exception in route_history view : RoutesHistory object query old_route is empty')
            #     # return Response({"Error: old_route history not available"}, status=status.HTTP_204_NO_CONTENT)
            #     return Response({"Error: old route history not available"},
            #                     status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # except Exception as e:
            #     logger.exception('exception in route_history view RoutesHistory object', e)
            #     return Response({"Error: In route_history - query set"},
            #                     status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

        try:
            # Get history
            route = RoutesHistory.objects.get(id=id)
            start_program_number, dest_program_number = sorted([route.start_program_number, route.dest_program_number])

            all_stops = StopsRoutes.objects.filter(route=route.route,
                                                   direction=route.direction,
                                                   program_number__range=(start_program_number,
                                                                          dest_program_number)
                                                   ).order_by('program_number')
            if not all_stops.exists():
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            logger.exception('exception in routes_history view : stops_routes object queryset all_stops is empty')
            # return Response({"Error: Bus record not available"}, status=status.HTTP_204_NO_CONTENT)
            return Response({"Error: Bus record not available"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.exception('exception in route_history view stops_routes object', e)
            return Response({"Error: In route_history - stops_routes query set"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create JSON response
        payload = []
        try:
            for stops in all_stops:
                stop_details = {'stop_id': stops.stop_id.stop_id, 'stop_name': stops.stop_id.stop_name,
                                'stop_lat': stops.stop_id.stop_lat,
                                'stop_lng': stops.stop_id.stop_lng,
                                'program_number': stops.program_number}
                payload.append(stop_details)
        except Exception as e:
            logger.exception('exception in route_history view while JSON payload generation', e)
            return Response({"Error: In route_history - valid JSON payload not generated"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return response
        try:
            return JsonResponse(payload, safe=False)
        except Exception as e:
            logger.exception('exception in route_history view while returning JSON response', e)
            return Response({"Error: In route_history - valid JSON response not returned"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
