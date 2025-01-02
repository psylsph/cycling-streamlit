import streamlit as st
import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
from datetime import datetime, timedelta, timezone

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

def display_weather_card(weather_data, day_offset=0):
    daily = weather_data.Daily()
    hourly = weather_data.Hourly()
    current = weather_data.Current()

    daily_time = range(daily.Time(), daily.TimeEnd(), daily.Interval())
    daily_variables = list(map(lambda i: daily.Variables(i), range(0, daily.VariablesLength())))
    
    temp_max_var = next(filter(lambda x: x.Variable() == 0 and x.Altitude() == 2, daily_variables), None)
    daily_temperature_2m_max = temp_max_var.ValuesAsNumpy() if temp_max_var else "NaN"
    
    temp_min_var = next(filter(lambda x: x.Variable() == 1 and x.Altitude() == 2, daily_variables), None)
    daily_temperature_2m_min = temp_min_var.ValuesAsNumpy() if temp_min_var else "NaN"
    
    weather_code_var = next(filter(lambda x: x.Variable() == 2, daily_variables), None)
    daily_weather_code = weather_code_var.ValuesAsNumpy() if weather_code_var else "NaN"
    
    wind_speed_var = next(filter(lambda x: x.Variable() == 3 and x.Altitude() == 10, daily_variables), None)
    daily_wind_speed_10m_max = wind_speed_var.ValuesAsNumpy() if wind_speed_var else "NaN"

    hourly_time = range(hourly.Time(), hourly.TimeEnd(), hourly.Interval())
    hourly_variables = list(map(lambda i: hourly.Variables(i), range(0, hourly.VariablesLength())))
    
    temp_2m_var = next(filter(lambda x: x.Variable() == 0 and x.Altitude() == 2, hourly_variables), None)
    hourly_temperature_2m = temp_2m_var.ValuesAsNumpy() if temp_2m_var else []
    
    precipitation_var = next(filter(lambda x: x.Variable() == 1, hourly_variables), None)
    hourly_precipitation = precipitation_var.ValuesAsNumpy() if precipitation_var else []
    
    wind_speed_var = next(filter(lambda x: x.Variable() == 2 and x.Altitude() == 10, hourly_variables), None)
    hourly_wind_speed_10m = wind_speed_var.ValuesAsNumpy() if wind_speed_var else []
    
    uv_index_var = next(filter(lambda x: x.Variable() == 3, hourly_variables), None)
    hourly_uv_index = uv_index_var.ValuesAsNumpy() if uv_index_var else []

    current_variables = list(map(lambda i: current.Variables(i), range(0, current.VariablesLength())))
    
    current_temperature_2m_var = next(filter(lambda x: x.Variable() == 0 and x.Altitude() == 2, current_variables), None)
    current_temperature_2m = current_temperature_2m_var.Value() if current_temperature_2m_var else "NaN"
    
    current_relative_humidity_2m_var = next(filter(lambda x: x.Variable() == 1 and x.Altitude() == 2, current_variables), None)
    current_relative_humidity_2m = current_relative_humidity_2m_var.Value() if current_relative_humidity_2m_var else "NaN"
    
    current_wind_speed_10m_var = next(filter(lambda x: x.Variable() == 2 and x.Altitude() == 10, current_variables), None)
    current_wind_speed_10m = current_wind_speed_10m_var.Value() if current_wind_speed_10m_var else "NaN"
    
    current_uv_index_var = next(filter(lambda x: x.Variable() == 3, current_variables), None)
    current_uv_index = current_uv_index_var.Value() if current_uv_index_var else "NaN"

    day_index = day_offset
    date = datetime.fromtimestamp(daily_time[day_index], timezone.utc).strftime("%b %d")
    day = datetime.fromtimestamp(daily_time[day_index], timezone.utc).strftime("%a")
    time_range_start = datetime.fromtimestamp(hourly_time[0], timezone.utc).strftime("%I:%M %p")
    time_range_end = datetime.fromtimestamp(hourly_time[-1], timezone.utc).strftime("%I:%M %p")
    time_range = f"{time_range_start}  {time_range_end}"
    temp_high = daily_temperature_2m_max[day_index]
    temp_low = daily_temperature_2m_min[day_index]
    conditions = daily_weather_code[day_index]
    wind = f"{daily_wind_speed_10m_max[day_index]} m/s"
    uv = f"Low"
    hourly_temps = {}
    for i in range(len(hourly_temperature_2m)):
        time = datetime.fromtimestamp(hourly_time[i], timezone.utc).strftime("%I:%M %p")
        hourly_temps[time] = hourly_temperature_2m[i]

    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            st.subheader(f"{day}, {date}")
            st.write(f"{time_range}")
            st.write(f"{temp_low}°")
            st.write(f"{conditions}")

        with col2:
            if temp_high == "NaN":
                st.markdown(f"<h1 style='text-align: center; color: red;'>{temp_high}</h1>", unsafe_allow_html=True)
            elif temp_high > 0:
                st.markdown(f"<h1 style='text-align: center; color: green;'>{temp_high}</h1>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h1 style='text-align: center; color: red;'>{temp_high}</h1>", unsafe_allow_html=True)
            if hourly_temps:
                for time, temp in hourly_temps.items():
                    if temp > 0:
                        st.markdown(f"<p style='text-align: center; color: green;'>{time} {temp}</p>", unsafe_allow_html=True)
                    elif temp < 0:
                        st.markdown(f"<p style='text-align: center; color: red;'>{time} {temp}</p>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<p style='text-align: center;'>{time} {temp}</p>", unsafe_allow_html=True)

        with col3:
            st.write(f"{wind}")
            st.write(f"UV {uv}")
            #if rain_chance:
            #    st.write(f"{rain_chance}")

        st.markdown("---")


weather_data = fetch_weather_data(latitude=52.52, longitude=13.41)

display_weather_card(weather_data, day_offset=0)
display_weather_card(weather_data, day_offset=1)
display_weather_card(weather_data, day_offset=2)
