import streamlit as st
import openmeteo_requests
from openmeteo_sdk.Variable import Variable
import requests_cache
from retry_requests import retry
import pandas as pd
from datetime import datetime, timedelta, timezone
import requests

st.set_page_config(page_title="Cycling Weather", layout="wide")

st.title("Rayne")

cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
om = openmeteo_requests.Client(session=retry_session)

def fetch_weather_data(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "precipitation", "wind_speed_10m", "uv_index"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "weather_code", "wind_speed_10m_max"],
        "current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "uv_index"]
    }
    responses = om.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
    response = responses[0]
    return response

def fetch_location():
    try:
        response = requests.get("https://ipapi.co/json/")
        #response.raise_for_status()
        data = response.json()
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        return latitude, longitude
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location: {e}")
        return None, None

def display_weather_card(weather_data, day_offset=0):
    
    hourly = weather_data.Hourly()
    hourly_time = range(hourly.Time(), hourly.TimeEnd(), hourly.Interval())
    hourly_variables = list(map(lambda i: hourly.Variables(i), range(0, hourly.VariablesLength())))

    hourly_temperature_2m = next(filter(lambda x: x.Variable() == Variable.temperature and x.Altitude() == 2, hourly_variables)).ValuesAsNumpy()
    hourly_precipitation = next(filter(lambda x: x.Variable() == Variable.precipitation, hourly_variables)).ValuesAsNumpy()
    hourly_wind_speed_10m = next(filter(lambda x: x.Variable() == Variable.wind_speed and x.Altitude() == 10, hourly_variables)).ValuesAsNumpy()


    hourly_time = range(hourly.Time(), hourly.TimeEnd(), hourly.Interval())
    hourly_variables = list(map(lambda i: hourly.Variables(i), range(0, hourly.VariablesLength())))
    
    temp_2m_var = next(filter(lambda x: x.Variable() == 0 and x.Altitude() == 2, hourly_variables), None)
    hourly_temperature_2m = temp_2m_var.ValuesAsNumpy() if temp_2m_var else None
    
    
    wind_speed_var = next(filter(lambda x: x.Variable() == 2 and x.Altitude() == 10, hourly_variables), None)
    hourly_wind_speed_10m = wind_speed_var.ValuesAsNumpy() if wind_speed_var else None
    
    uv_index_var = next(filter(lambda x: x.Variable() == 3, hourly_variables), None)
    hourly_uv_index = uv_index_var.ValuesAsNumpy() if uv_index_var else None

    # day_index = day_offset
    # date = datetime.fromtimestamp(daily_time[day_index], timezone.utc).strftime("%b %d")
    # day = datetime.fromtimestamp(daily_time[day_index], timezone.utc).strftime("%a")
    # time_range_start = datetime.fromtimestamp(hourly_time[0], timezone.utc).strftime("%I:%M %p")
    # time_range_end = datetime.fromtimestamp(hourly_time[-1], timezone.utc).strftime("%I:%M %p")
    # time_range = f"{time_range_start}  {time_range_end}"
    # temp_high = daily_temperature_2m_max[day_index] if daily_temperature_2m_max is not None and len(daily_temperature_2m_max) > day_index else "NaN"
    # temp_low = daily_temperature_2m_min[day_index] if daily_temperature_2m_min is not None and len(daily_temperature_2m_min) > day_index else "NaN"
    # conditions = daily_weather_code[day_index] if daily_weather_code is not None and len(daily_weather_code) > day_index else "NaN"
    # wind = f"{daily_wind_speed_10m_max[day_index]} m/s" if daily_wind_speed_10m_max is not None and len(daily_wind_speed_10m_max) > day_index else "NaN"
    # uv = f"Low"
    # hourly_temps = {}
    # if hourly_temperature_2m is not None and len(hourly_temperature_2m) > 0:
    #     for i in range(len(hourly_temperature_2m)):
    #         time = datetime.fromtimestamp(hourly_time[i], timezone.utc).strftime("%I:%M %p")
    #         hourly_temps[time] = hourly_temperature_2m[i]

    # with st.container():
    #     col1, col2, col3 = st.columns([1, 2, 1])

    #     with col1:
    #         st.subheader(f"{day}, {date}")
    #         st.write(f"{time_range}")
    #         st.write(f"{temp_low}°")
    #         st.write(f"{conditions}")

    #     with col2:
    #         if temp_high == "NaN":
    #             st.markdown(f"<h1 style='text-align: center; color: red;'>{temp_high}</h1>", unsafe_allow_html=True)
    #         else:
    #             try:
    #                 temp_high_float = float(temp_high)
    #                 if temp_high_float > 0:
    #                     st.markdown(f"<h1 style='text-align: center; color: green;'>{temp_high}</h1>", unsafe_allow_html=True)
    #                 else:
    #                     st.markdown(f"<h1 style='text-align: center; color: red;'>{temp_high}</h1>", unsafe_allow_html=True)
    #             except ValueError:
    #                 st.markdown(f"<h1 style='text-align: center; color: red;'>{temp_high}</h1>", unsafe_allow_html=True)
    #         if hourly_temps:
    #             for time, temp in hourly_temps.items():
    #                 if temp > 0:
    #                     st.markdown(f"<p style='text-align: center; color: green;'>{time} {temp}</p>", unsafe_allow_html=True)
    #                 elif temp < 0:
    #                     st.markdown(f"<p style='text-align: center; color: red;'>{time} {temp}</p>", unsafe_allow_html=True)
    #                 else:
    #                     st.markdown(f"<p style='text-align: center;'>{time} {temp}</p>", unsafe_allow_html=True)

    #     with col3:
    #         st.write(f"{wind}")
    #         st.write(f"UV {uv}")
    #         #if rain_chance:
    #         #    st.write(f"{rain_chance}")

    #     st.markdown("---")

latitude, longitude = fetch_location()
if latitude and longitude:
    st.write(f"Latitude: {latitude}", f"Longitude: {longitude}")
    weather_data = fetch_weather_data(latitude=latitude, longitude=longitude)

    display_weather_card(weather_data, day_offset=0)
    display_weather_card(weather_data, day_offset=1)
    display_weather_card(weather_data, day_offset=2)
else:
    st.error("Could not fetch location. Please ensure you have an internet connection.")
