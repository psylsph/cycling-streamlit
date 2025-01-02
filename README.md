# Cycling Weather App

This is a Streamlit app that displays weather information for cycling.

## Features

- Fetches weather data using the Open-Meteo API.
- Displays weather cards for the current day and the next two days.
- Shows high and low temperatures, conditions, wind speed, and UV index.
- Highlights hourly temperatures in green if above 60 and red if below 0.

## How to run

1.  Install the required libraries:
    ```bash
    pip install streamlit openmeteo-requests requests_cache
    ```
2.  Run the app:
    ```bash
    streamlit run app.py
    ```
