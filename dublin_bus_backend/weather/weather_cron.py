import requests
from weather.models import Weather
from datetime import datetime

# Open Weather API URL
WEATHER_URL = "http://api.openweathermap.org/data/2.5/forecast"
WEATHER_PARAMS = {'appid': "0b877c10f2c8044a1668be4f89c01784", 'id': '2964574'}


def weather_cron_job():
    try:
        # Make API request to Open Weather and get response in JSON
        response = requests.get(url=WEATHER_URL, params=WEATHER_PARAMS).json()

        # Check for response code
        if response['cod'] == "200":
            # Iterating the predictions
            for predictions in response['list']:
                try:
                    # Convert the required values
                    date_weather_in_date = datetime.fromtimestamp(predictions['dt'])
                    date_weather = date_weather_in_date.strftime('%Y-%m-%d')
                    hour_of_day = date_weather_in_date.hour
                    feels_like = str(round(predictions['main']['feels_like'] - 273.15))
                    wind_speed = str(round(predictions['wind']['speed']))
                    weather_id = str(predictions['weather'][0]['id'])
                    temperature = str(round(predictions['main']['temp'] - 273.15))
                    temperature_min = str(round(predictions['main']['temp_min'] - 273.15))
                    temperature_max = str(round(predictions['main']['temp_max'] - 273.15))
                    humidity = predictions['main']['humidity']
                    weather_main = predictions['weather'][0]['main']
                    weather_description = predictions['weather'][0]['description']

                    # Create/update in db
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
                except Exception as e:
                    print('exception in weather_cron_job for loop', e)
    except Exception as e:
        print('exception in weather_cron_job', e)
