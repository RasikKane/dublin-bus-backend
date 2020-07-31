import requests
from weather.models import Weather
from datetime import datetime, timedelta

# Open Weather API URL
WEATHER_URL = "http://api.openweathermap.org/data/2.5/forecast"
WEATHER_PARAMS = {'appid': "0b877c10f2c8044a1668be4f89c01784", 'id': '2964574'}


def save_update_weather_data(date_weather, hour_of_day, feels_like, wind_speed, weather_id, temperature,
                             temperature_min, temperature_max, humidity, weather_main,
                             weather_description):
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


def weather_cron_job():
    try:
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
                    save_update_weather_data(date_weather, hour_of_day, feels_like, wind_speed, weather_id, temperature,
                                             temperature_min, temperature_max, humidity, weather_main,
                                             weather_description)

                    # for last entry in cron job; we need additional 3 hour data; same data for last hr is repeated
                    if count == len_list:
                        print("count == len_list")
                        for i in range(3):
                            hour_of_day = hour_of_day + 1
                            # Save in db
                            save_update_weather_data(date_weather, hour_of_day, feels_like, wind_speed, weather_id,
                                                     temperature,
                                                     temperature_min, temperature_max, humidity, weather_main,
                                                     weather_description)

                    # 1st 3 hr data for a day = Extended [23,24,25] hr data for last day
                    elif hour_of_day in [0, 1, 2]:
                        hour_of_day = hour_of_day + 24
                        date_weather = (date_weather_in_date - timedelta(days=1)).strftime('%Y-%m-%d')
                        # Save in db
                        save_update_weather_data(date_weather, hour_of_day, feels_like, wind_speed, weather_id,
                                                 temperature,
                                                 temperature_min, temperature_max, humidity, weather_main,
                                                 weather_description)
                except Exception as e:
                    # print('exception in weather_cron_job for loop', e)
                    pass
    except Exception as e:
        # print('exception in weather_cron_job', e)
        pass
