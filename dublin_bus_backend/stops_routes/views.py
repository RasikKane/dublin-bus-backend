from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from line_prognumber.models import LinesPrognumbers
from stops_routes.models import StopsRoutes
import logging

# Create a logger for this file
logger = logging.getLogger(__file__)


class RoutesPerBusNumber(APIView):

    def get(self, request):

        try:
            # Getting source prog no
            source_prog_number = StopsRoutes.objects.get(stop_id=request.query_params.get('stop_id'),
                                                         route=request.query_params.get('bus_number'),
                                                         direction=request.query_params.get('direction'))

            # Getting end prog no
            end_prog_number = LinesPrognumbers.objects.get(line_id=request.query_params.get('bus_number'),
                                                           direction=request.query_params.get('direction'))

            # start_program_number, dest_program_number = sorted([source_prog_number.program_number,
            #                                                     end_prog_number.last_program_number])

            # if request.query_params.get('is_destination_toggled') == "false":
            #     all_stops = StopsRoutes.objects.filter(route=request.query_params.get('bus_number'),
            #                                            direction=request.query_params.get('direction'),
            #                                            program_number__range=(start_program_number,
            #                                                                   dest_program_number)
            #                                            ).order_by('program_number')
            #
            # else:
            #     all_stops = StopsRoutes.objects.filter(route=request.query_params.get('bus_number'),
            #                                            direction=request.query_params.get('direction'),
            #                                            program_number__range=(start_program_number,
            #                                                                   dest_program_number)
            #                                            ).order_by('-program_number')

            if request.query_params.get('is_destination_toggled') == "false":
                # Checking the small/large prog no
                if source_prog_number.program_number < end_prog_number.last_program_number:
                    all_stops = StopsRoutes.objects.filter(route=request.query_params.get('bus_number'),
                                                           direction=request.query_params.get('direction'),
                                                           program_number__range=(source_prog_number.program_number,
                                                                                  end_prog_number.last_program_number)
                                                           ).order_by('program_number')
                else:
                    all_stops = StopsRoutes.objects.filter(route=request.query_params.get('bus_number'),
                                                           direction=request.query_params.get('direction'),
                                                           program_number__range=(end_prog_number.last_program_number,
                                                                                  source_prog_number.program_number)
                                                           ).order_by('program_number')
            else:
                # Checking the small/large prog no
                if source_prog_number.program_number < end_prog_number.first_program_number:
                    all_stops = StopsRoutes.objects.filter(route=request.query_params.get('bus_number'),
                                                           direction=request.query_params.get('direction'),
                                                           program_number__range=(source_prog_number.program_number,
                                                                                  end_prog_number.first_program_number)
                                                           ).order_by('-program_number')
                else:
                    all_stops = StopsRoutes.objects.filter(route=request.query_params.get('bus_number'),
                                                           direction=request.query_params.get('direction'),
                                                           program_number__range=(end_prog_number.first_program_number,
                                                                                  source_prog_number.program_number)
                                                           ).order_by('-program_number')

        except Exception as e:
            logger.exception('exception in stops_routes view StopsRoutes object', e)
            return Response({"Error: In stops_routes -  query set"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            logger.exception('exception in stops_routes view while JSON payload generation', e)
            return Response({"Error: In stops_routes - valid JSON payload not generated"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return response
        try:
            return JsonResponse(payload, safe=False)
        except Exception as e:
            logger.exception('exception in stops_routes view while returning JSON response', e)
            return Response({"Error: In stops_route - valid JSON response not returned"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
