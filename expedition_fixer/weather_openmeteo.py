import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from timezonefinder import TimezoneFinder

from dateutil import parser

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

def getWeatherForLocation(lat, lng, start_date, end_date ):
    tf = TimezoneFinder()
    tz = tf.timezone_at(lat=lat, lng=lng)
    #print(f'{tz}    ')

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lng,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "hourly": ["temperature_2m", "apparent_temperature", "wind_speed_10m", "wind_direction_10m"],
        "timeformat": "unixtime",
        "timezone": tz
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    #print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
    #print(f"Elevation {response.Elevation()} m asl")
    #print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    #print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_apparent_temperature = hourly.Variables(1).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(2).ValuesAsNumpy()
    hourly_wind_direction_10m = hourly.Variables(3).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s"),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s"),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["apparent_temperature"] = hourly_apparent_temperature
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["wind_direction_10m"] = hourly_wind_direction_10m

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    #print(hourly_dataframe)
    return hourly_dataframe

#get temp for a point and time
def getTempForTime(trkpt_time, hourly_dataframe):
    #trkpt_time = parser.parse(iso_time_str )
    rounded_time = pd.Timestamp(trkpt_time).round('60min').to_pydatetime()
    temp = None
    time_str = rounded_time.strftime('%Y-%m-%d %H:%M:%S')

    point_temps = hourly_dataframe.loc[hourly_dataframe['date'] == time_str]["temperature_2m"].values  
    if point_temps.size > 0:
        temp = round(point_temps[0],2)
        #print(temp)
    else:
        print(f'No data for {trkpt_time}')
    return temp


weather = getWeatherForLocation(lat=68.758494891346, lng=26.233359984518, start_date=pd.to_datetime('2023-12-31'), end_date=pd.to_datetime('2024-01-06'))

temp = getTempForTime(trkpt_time='2023-12-31T01:00:00Z', hourly_dataframe=weather)

#print(f'{weather.head(10)}')
#print(f'{temp}')