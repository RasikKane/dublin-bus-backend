from django.http import JsonResponse
from django.contrib.admin.utils import flatten
from django.utils import dateparse
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from timetable.models import Timetable
from stops_routes.models import StopsRoutes
from weather.models import Weather
from routes_history.models import RoutesHistory
from bus_stops.models import BusStops
# import sklearn
import pandas as pd
import pickle
from math import ceil
from numpy import concatenate
import csv
from datetime import datetime
import logging

# Create a logger for this file
logger = logging.getLogger(__file__)


# Create your views here.

class PredictArrivalTime(APIView):

    def post(self, request):
        """
        :param request:{'route', 'direction', 'start_stop_id', 'dest_stop_id', 'start_program_number',
        'dest_program_number', 'datetime_input', 'isFromRecentRoutes', 'user_id'};
        return json_response: {'stop_id', 'stop_name', 'stop_lat', 'stop_lng',
        'program_number', 'arrival_time', 'section_travel_time' }
        """
        # resolve datetime stamp into parameters required for input to  prediction algorithm
        dt_in = dateparse.parse_datetime(str(request.data.get('datetime_input')))
        if not isinstance(dt_in, datetime):
            logger.exception('invalid datetime_input')
            return Response({"Datetime format is not valid"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # date, hr_date : used for extracting weather parameters for next 3 hours from supplies hr_date on given date
        date, hr_date = str(dt_in.date()), dt_in.hour
        sec_date, min_date = dt_in.second, dt_in.minute
        # month, day_of_week, quarter,tArr : features in prediction model input
        month, day_of_week, quarter = dt_in.month, dt_in.weekday(), int(ceil(dt_in.month / 3.))
        tArr = sec_date + min_date * 60 + hr_date * 3600

        # temporary variables for testing
        # month, quarter = 1, 1
        # date = "2018-01-01"

        # Obtain weather data for remaining hours from given hour for fields : [feels_like,wind_speed, weather_id]
        try:
            weather = Weather.objects.filter(date_weather=date,
                                             hour_of_day__range=(hr_date, 26)
                                             ).order_by('hour_of_day').values('feels_like', 'wind_speed', 'weather_id')
            if not weather.exists():
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            logger.exception('exception in timetable view : weather object queryset weather is empty')
            # return Response({"Weather not available"}, status=status.HTTP_204_NO_CONTENT)
            return Response({"Future weather not available"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.exception('exception in timetable view weather object', e)
            return Response({"Future weather not available"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Check if request is from recent routes or not.
        flag_recentRoute = request.data.get('isFromRecentRoutes')
        if not flag_recentRoute:
            start_program_number, dest_program_number = sorted([request.data.get('start_program_number'),
                                                                request.data.get('dest_program_number')])
            line = request.data.get('route')
            direction = request.data.get('direction')

        else:
            # Get history
            try:
                route = RoutesHistory.objects.get(id=request.data.get('id'))
            except route.DoesNotExist:
                logger.exception('exception in timetable view : RoutesHistory object queryset route is empty')
                # return Response({"Recent route not available"}, status=status.HTTP_204_NO_CONTENT)
                return Response({"Recent route not available"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            start_program_number, dest_program_number = sorted([route.start_program_number, route.dest_program_number])
            line = route.route
            direction = route.direction

        # Generate  query set for combination of STOPPOINTID - PROGRNUMBER
        try:
            stops_prog = StopsRoutes.objects.filter(route=line,
                                                    direction=direction,
                                                    program_number__range=(start_program_number,
                                                                           dest_program_number)
                                                    ).order_by('program_number')

            # Generate list of stop Id and program numbers used for prediction
            stops_list = flatten(stops_prog.values_list('stop_id'))
            progr_list = flatten(stops_prog.values_list('program_number'))

            if not stops_prog.exists():
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            logger.exception('exception in timetable view : stops_routes object queryset stops_prog is empty')
            # return Response({"Bus not available"}, status=status.HTTP_204_NO_CONTENT)
            return Response({"Bus not available"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.exception('exception in timetable view stops_routes object', e)
            return Response({"Bus not available"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Generate  query set for combination of LINEID - DIRECTION
        try:
            line_direction = Timetable.objects.filter(line_id=line,
                                                      direction=direction,
                                                      planned_arrival__gt=tArr
                                                      ).order_by('planned_arrival').values('stop_id', 'line_id',
                                                                                           'direction',
                                                                                           'program_number',
                                                                                           'planned_arrival')
            if not line_direction.exists():
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            logger.exception('exception in timetable view : timetable object queryset line_direction is empty'
                             'Route: {}, Direction:{}, Time:{}'.format(str(line), str(direction),
                                                                       str(str(hr_date) + ":" + str(min_date)))
                             )
            # return Response({"Bus Timetable not available"}, status=status.HTTP_204_NO_CONTENT)
            return Response({"Bus not available"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.exception('exception in timetable view timetable object', e)
            return Response({"Bus not available"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # dataframe for bus timetable
        df_line_direction = pd.DataFrame.from_records(line_direction)
        if df_line_direction.empty:
            logger.exception('No bus scheduled in timetable : df_line_direction is empty. '
                             'Route: {}, Direction:{}, Time:{}'.format(str(line), str(direction),
                                                                       str(str(hr_date) + ":" + str(min_date))))
            # return Response({"Bus not available"}, status=status.HTTP_204_NO_CONTENT)
            return Response({"Bus not available"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # schema for input dataframe to model
        df_X = pd.DataFrame(
            columns=['month', 'dayofweek_num', 'quarter', 'PROGRNUMBER', 'STOPPOINTID', 'PLANNEDTIME_ARR',
                     'feels_like', 'wind_speed', 'weather_id'])
        convert_dict = {'month': 'int', 'dayofweek_num': 'int', 'quarter': 'int',
                        'PROGRNUMBER': 'int', 'STOPPOINTID': 'int', 'PLANNEDTIME_ARR': 'int',
                        'feels_like': 'float', 'wind_speed': 'float', 'weather_id': 'int'
                        }

        # Obtain planned arrival time for eac stop ID and generate dataframe to pass to ML input
        try:
            for stop, progr_number in zip(stops_list, progr_list):
                list_timeArr = sorted(df_line_direction.query('stop_id == @stop')['planned_arrival'].to_list())
                TIME_ARR = next(TIME_ARR for TIME_ARR in list_timeArr if TIME_ARR > tArr)
                # Append tuple to dataframe
                df_X.loc[len(df_X)] = [month, day_of_week, quarter, progr_number, stop, TIME_ARR,
                                       *weather.get(hour_of_day=int(TIME_ARR / 3600)).values()]
                # Assign TIME_ARR of present stop to tArr; this is base time to calculate PLANNEDTIME_ARR of next stop
                tArr = TIME_ARR
        except Exception as e:
            logger.exception('exception in timetable view df_X preparation', e)
            return Response({"Bus not available after given time"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Typecast dataframe
        try:
            df_X = df_X.astype(convert_dict)
        except Exception as e:
            logger.exception('exception in timetable view df_X type casting', e)
            return Response({"Sorry! Something went wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Fetch prediction model
        filename = "./models/" + str(line) + "_" + str(direction) + ".pkl"
        try:
            model = pickle.load(open(filename, 'rb'))
        except Exception as e:
            logger.exception('exception while fetching model', e)
            return Response({"Sorry! Something went wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            prediction = model.predict(df_X)
            # format output for generating JSON And append dummy entry for travel_time calculation
            prediction = list(map(round, concatenate(prediction).flat))
            # prediction = [round(pred) for pred_list in prediction for pred in pred_list]
            prediction.append(0)
        except Exception as e:
            logger.exception('exception during prediction', e)
            return Response({"Sorry! Something went wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Define payload and return prediction response for each stop id
        payload = []

        try:
            for index, stops in enumerate(stops_prog):
                stop_details = {'stop_id': stops.stop_id.stop_id,
                                'stop_name': stops.stop_id.stop_name,
                                'stop_lat': stops.stop_id.stop_lat,
                                'stop_lng': stops.stop_id.stop_lng,
                                'program_number': stops.program_number,
                                'arrival_time': prediction[index],
                                'section_travel_time': prediction[index + 1] - prediction[index]
                                }
                payload.append(stop_details)
        except Exception as e:
            logger.exception('exception in timetable view while JSON payload generation', e)
            return Response({"Sorry! Something went wrong!"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            return JsonResponse(payload, safe=False)
        except Exception as e:
            logger.exception('exception in timetable view while returning JSON response', e)
            return Response({"Sorry! Something went wrong!"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TimetableDB(APIView):
    def get(self, request):
        try:
            with open(request.data.get('timetableCSV')) as f:
                print(request.data.get('timetableCSV'))
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    try:
                        _, created = Timetable.objects.get_or_create(
                            line_id=row[0],
                            direction=row[1],
                            stop_id=BusStops.objects.get(stop_id=row[2]),
                            program_number=row[3],
                            planned_arrival=row[4]
                        )
                    except IntegrityError:
                        continue
            return Response({"message": "Data entry for TIMETABLE successful"}, status=status.HTTP_200_OK)

        # reference for deciding status code : stack-overflow
        # https://stackoverflow.com/questions/3290182/rest-http-status-codes-for-failed-validation-or-invalid-duplicate
        except Exception as e:
            logger.exception('exception during Data entry in TIMETABLE database ', e)
            return Response({"Error": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
