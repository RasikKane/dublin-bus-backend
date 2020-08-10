import requests
# from rest_framework.response import Response
# from rest_framework import status
from weather.models import Weather
from datetime import datetime, timedelta
from django import db
import logging

# Create a logger for this file
logger = logging.getLogger(__file__)

# Open Weather API URL
WEATHER_URL = "http://api.openweathermap.org/data/2.5/forecast"
WEATHER_PARAMS = {'appid': "0b877c10f2c8044a1668be4f89c01784", 'id': '2964574'}


def save_update_weather_data(date_weather, hour_of_day, feels_like, wind_speed, weather_id, temperature,
                             temperature_min, temperature_max, humidity, weather_main,
                             weather_description):
    try:
        obj, created = Weather.objects.update_or_create(
            date_weather=date_weather, hour_of_day=hour_of_day,
            defaults={
                'feels_like': feels_like,
                'wind_speed': wind_speed,
                'weather_id': weather_id,
                'temp': temperature,
                'temp_min': temperature_min,
                'temp_max': temperature_max,
                'humidity': humidity,
                'weather_main': weather_main,
                'weather_description': weather_description
            },
        )

    # reference for deciding status code : stack-overflow
    # https://stackoverflow.com/questions/3290182/rest-http-status-codes-for-failed-validation-or-invalid-duplicate
    except Exception as e:
        logger.error('exception in weather view Weather object')
        logger.exception(e)
        # return Response({"Error: update_or_create"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


def weather_cron_job():
    try:
        db.connections.close_all()
        logger.info("Running schedular")

        # Make API request to Open Weather and get response in JSON
        response = requests.get(url=WEATHER_URL, params=WEATHER_PARAMS).json()

        # Check for response code
        if response['cod'] == "200":
            len_list = len(response['list'])

            # Iterating the predictions
            for count, predictions in enumerate(response['list'], start=1):
                try:
                    # Convert the required values
                    date_weather_in_date = datetime.fromtimestamp(predictions['dt'])
                    date_weather = date_weather_in_date.strftime('%Y-%m-%d')
                    hour_of_day = date_weather_in_date.hour
                    feels_like = "{:.1f}".format(predictions['main']['feels_like'] - 273.15)
                    wind_speed = "{:.1f}".format(predictions['wind']['speed'])
                    weather_id = str(predictions['weather'][0]['id'])
                    temperature = "{:.1f}".format(predictions['main']['temp'] - 273.15)
                    temperature_min = "{:.1f}".format(predictions['main']['temp_min'] - 273.15)
                    temperature_max = "{:.1f}".format(predictions['main']['temp_max'] - 273.15)
                    humidity = predictions['main']['humidity']
                    weather_main = predictions['weather'][0]['main']
                    weather_description = predictions['weather'][0]['description']

                    # Make default first entry
                    # save_update_weather_data(date_weather, hour_of_day, feels_like, wind_speed, weather_id,
                    #                          temperature, temperature_min, temperature_max, humidity, weather_main,
                    #                          weather_description)

                    # # for last entry in cron job; we need additional 3 hour data; same data for last hr is repeated
                    # if count == len_list:
                    #     for i in range(3):
                    #         hour_of_day = hour_of_day + 1
                    #         # Save in db
                    #         save_update_weather_data(date_weather, hour_of_day, feels_like, wind_speed, weather_id,
                    #                                  temperature,
                    #                                  temperature_min, temperature_max, humidity, weather_main,
                    #                                  weather_description)
                    #
                    # # 1st 3 hr data for a day = Extended [23,24,25] hr data for last day
                    # elif hour_of_day in [0, 1, 2]:
                    #     hour_of_day = hour_of_day + 24
                    #     date_weather = (date_weather_in_date - timedelta(days=1)).strftime('%Y-%m-%d')
                    #     # Save in db
                    #     save_update_weather_data(date_weather, hour_of_day, feels_like, wind_speed, weather_id,
                    #                              temperature,
                    #                              temperature_min, temperature_max, humidity, weather_main,
                    #                              weather_description)

                    # if count == len_list:
                    for _ in range(3):
                        # Save in db
                        save_update_weather_data(date_weather, hour_of_day, feels_like, wind_speed, weather_id,
                                                 temperature, temperature_min, temperature_max, humidity, weather_main,
                                                 weather_description)

                        # 1st 3 hr data for a day = Extended [23,24,25] hr data for last day
                        if hour_of_day in [0, 1, 2]:
                            ext_hour_of_day = hour_of_day + 24
                            ext_date_weather = (date_weather_in_date - timedelta(days=1)).strftime('%Y-%m-%d')
                            # Save in db
                            save_update_weather_data(ext_date_weather, ext_hour_of_day, feels_like, wind_speed,
                                                     weather_id, temperature, temperature_min, temperature_max,
                                                     humidity, weather_main, weather_description)

                        hour_of_day = hour_of_day + 1

                except Exception as e:
                    logger.error('exception in weather_cron_job for loop')
                    logger.exception(e)
    except Exception as e:
        logger.error('exception in weather_cron_job')
        logger.exception(e)
