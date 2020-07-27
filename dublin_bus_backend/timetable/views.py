from django.http import JsonResponse
from rest_framework.views import APIView
from timetable.models import timetable
from stops_routes.models import StopsRoutes
from weather.models import Weather
import pandas as pd
import pickle
from django.contrib.admin.utils import flatten
from django.utils import dateparse
from math import ceil
from routes_history.models import RoutesHistory
from numpy import concatenate, rint


# from rest_framework.response import Response
# from rest_framework import status
# import sklearn


# Create your views here.

class PredictArrivalTime(APIView):

    def post(self, request):
        """
        :param request:[datetime, route, direction, start_stop_id, dest_stop_id] ;
        return json_response: {'stop_id', 'stop_name', 'stop_lat', 'stop_lng',
        'program_number', 'arrival_time', 'section_travel_time' }
        """
        # resolve datetime stamp into parameters required for input to  prediction algorithm
        dt_in = dateparse.parse_datetime(str(request.data.get('datetime_input')))
        # date, hr_date : used for extracting weather parameters for next 3 hours from supplies hr_date on given date
        date, hr_date = str(dt_in.date()), dt_in.hour
        # year, month, day_of_week, quarter,tArr : features in prediction model input
        year, month, day_of_week, quarter = dt_in.year, dt_in.month, dt_in.weekday(), int(ceil(dt_in.month / 3.))
        tArr = dt_in.second + dt_in.minute * 60 + hr_date * 3600

        # temporary variables for testing
        year, month, quarter = 2018, 1, 1
        date = "2018-01-01"

        # Obtain weather data for uptill 3 hours from given hour for fields : [feels_like,wind_speed, weather_id]
        # No dublin bus ride exceeds 3 hour planned journey, hence 3 entries from given input hour are selected
        weather = Weather.objects.filter(date_entry=date,
                                         hour_Day__range=(hr_date, hr_date + 3)
                                         ).order_by('hour_Day').values('feels_like', 'wind_speed', 'weather_id')

        # Check if request is from recent routes or not.
        flag_recentRoute = request.data.get('isFromRecentRoutes')
        if not flag_recentRoute:
            start_program_number, dest_program_number = sorted([request.data.get('start_program_number'),
                                                                request.data.get('dest_program_number')])

            stops_prog = StopsRoutes.objects.filter(route=request.data.get('route'),
                                                    direction=request.data.get('direction'),
                                                    program_number__range=(start_program_number,
                                                                           dest_program_number)
                                                    ).order_by('program_number')

            # Generate  query set for combination of LINEID - DIRECTION
            line_direction = timetable.objects.filter(line_id=request.data.get('route'),
                                                      direction=request.data.get('direction'),
                                                      planned_arrival__gt=tArr
                                                      ).order_by('planned_arrival').values('stop_id', 'line_id',
                                                                                           'direction',
                                                                                           'program_number',
                                                                                           'planned_arrival')
        else:
            # Get history
            route = RoutesHistory.objects.get(id=request.data.get('id'))
            start_program_number, dest_program_number = sorted([route.start_program_number, route.dest_program_number])

            stops_prog = StopsRoutes.objects.filter(route=route.route,
                                                    direction=route.direction,
                                                    program_number__range=(start_program_number,
                                                                           dest_program_number)
                                                    ).order_by('program_number')

            # Generate pandas dataframe from query set for combination of LINEID - DIRECTION
            line_direction = timetable.objects.filter(line_id=route.route,
                                                      direction=route.direction,
                                                      planned_arrival__gt=tArr
                                                      ).order_by('planned_arrival').values('stop_id', 'line_id',
                                                                                           'direction',
                                                                                           'program_number',
                                                                                           'planned_arrival')

        # dataframe for bus timetable
        df_line_direction = pd.DataFrame.from_records(line_direction)

        # input dataframe to model
        df_X = pd.DataFrame(
            columns=['year', 'month', 'dayofweek_num', 'quarter', 'PROGRNUMBER', 'STOPPOINTID', 'PLANNEDTIME_ARR',
                     'feels_like', 'wind_speed', 'weather_id'])
        convert_dict = {'year': 'int', 'month': 'int', 'dayofweek_num': 'int', 'quarter': 'int',
                        'PROGRNUMBER': 'int', 'STOPPOINTID': 'int', 'PLANNEDTIME_ARR': 'int',
                        'feels_like': 'float', 'wind_speed': 'float', 'weather_id': 'int'
                        }

        # Generate list of stop Id and program numbers used for prediction
        stops_list = flatten(stops_prog.values_list('stop_id'))
        progr_list = flatten(stops_prog.values_list('program_number'))

        # Obtain planned arrival time for eac stop ID and generate dataframe to pass to ML input
        for stop, progr_number in zip(stops_list, progr_list):
            list_timeArr = sorted(df_line_direction.query('stop_id == @stop')['planned_arrival'].to_list())
            TIME_ARR = next(TIME_ARR for TIME_ARR in list_timeArr if TIME_ARR > tArr)

            # Append tuple to dataframe
            df_X.loc[len(df_X)] = [year, month, day_of_week, quarter, progr_number, stop, TIME_ARR,
                                   *weather.get(hour_Day=int(TIME_ARR / 3600)).values()]

            # Assign TIME_ARR of present stop to tArr; this is base time for calculating PLANNEDTIME_ARR of next stop
            tArr = TIME_ARR

        # Typecast dataframe
        df_X = df_X.astype(convert_dict)

        # Fetch prediction model
        if not flag_recentRoute:
            filename = "./models/" + str(request.data.get('route')) + "_" +\
                       str(request.data.get('direction')) + ".pkl"
        else:
            filename = "./models/" + str(route.route) + "_" + str(route.direction) + ".pkl"

        model = pickle.load(open(filename, 'rb'))
        prediction = model.predict(df_X)

        # format output for generating JSON
        # prediction = [round(pred) for pred_list in prediction for pred in pred_list]
        prediction = list(map(round, concatenate(prediction).flat))

        # append dummy entry for travel_time calculation
        prediction.append(0)

        # Define payload and return prediction response for each stop id
        payload = []

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

        return JsonResponse(payload, safe=False)

# class PredictArrivalTime(APIView):
#
#     def post(self, request):
#     """ :param request:[datetime, route, direction, start_stop_id, dest_stop_id]
#     :return: json
#     response {'stop_id', 'stop_name', 'stop_lat', 'stop_lng', 'program_number', 'prediction', 'travel_time'} """
#
#             # Get program numbers for start_stop_id, dest_stop_id
#             start_program_number = StopsRoutes.objects.get(route=request.data.get('route'),
#                                                            direction=request.data.get('direction'),
#                                                            stop_id=request.data.get('start_stop_id'))
#
#             dest_program_number = StopsRoutes.objects.get(route=request.data.get('route'),
#                                                           direction=request.data.get('direction'),
#                                                           stop_id=request.data.get('dest_stop_id'))
#
#             print(start_program_number.program_number, dest_program_number.program_number)
#
#             stops_prog = StopsRoutes.objects.filter(route=request.data.get('route'),
#                                                     direction=request.data.get('direction'),
#                                                     program_number__range=(start_program_number,
#                                                                            dest_program_number)
#                                                     ).order_by('program_number')
#
#             """resolve datetime stamp into parameters required for input to  prediction algorithm"""
#             dt_in = dateparse.parse_datetime(str(request.data.get('datetime_input')))
#             year, month, day_of_week, quarter = dt_in.year, dt_in.month, dt_in.weekday(), int(ceil(dt_in.month / 3.))
#             tArr = dt_in.second + dt_in.minute * 60 + dt_in.hour * 3600
#
#             df_X = pd.DataFrame(
#                 columns=['year', 'month', 'dayofweek_num', 'quarter', 'PROGRNUMBER', 'STOPPOINTID', 'PLANNEDTIME_ARR'])
#
#             for stop in stops_prog:
#                 TIME_ARR = timetable.objects.filter(line_id=stop.route,
#                                                     stop_id=stop.stop_id.stop_id,
#                                                     direction=stop.direction,
#                                                     planned_arrival__gt=tArr,
#                                                     ).order_by('planned_arrival')[0]
#
#                 # list_timeArr = sorted(df_TIMETABLE.query('STOPPOINTID == @stop')['PLANNEDTIME_ARR'].to_list())
#                 # TIME_ARR = next(TIME_ARR for TIME_ARR in list_timeArr if TIME_ARR > t)
#
#                 # Assign TIME_ARR of present stop to tArr; this is base time for calculating PLANNEDTIME_ARR of next stop
#                 tArr = TIME_ARR.planned_arrival
#
#                 # Append tuple to dataframe
#                 df_X.loc[len(df_X)] = [year, month, day_of_week, quarter, stop.program_number, stop.stop_id.stop_id, tArr]
#                 # # Assign TIME_ARR of last STOP to t
#                 # t = TIME_ARR[0].planned_arrival
#                 # print(t)
#
#             # # Fetch prediction model
#             filename = "./models/" + str(request.data.get('route')) + "_" + str(request.data.get('direction')) + ".pkl"
#             model = pickle.load(open(filename, 'rb'))
#             prediction = model.predict(df_X)
#
#             # format output for generating JSON
#             prediction = [round(pred) for pred_list in prediction for pred in pred_list]
#             # append dummy entry for travel_time calculation
#             prediction.append(0)
#
#             # Define payload
#             payload = []
#
#             for index, stops in enumerate(stops_prog):
#                 stop_details = {'stop_id': stops.stop_id.stop_id,
#                                 'stop_name': stops.stop_id.stop_name,
#                                 'stop_lat': stops.stop_id.stop_lat,
#                                 'stop_lng': stops.stop_id.stop_lng,
#                                 'program_number': stops.program_number,
#                                 'prediction': prediction[index],
#                                 'travel_time': prediction[index + 1] - prediction[index]
#                                 }
#                 payload.append(stop_details)
#
#             return JsonResponse(payload, safe=False)