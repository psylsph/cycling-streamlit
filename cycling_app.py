import streamlit as st
import requests
from datetime import datetime, timedelta
import os

# OpenWeatherMap API key (replace with your own key)
OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")

# Function to fetch weather data
def get_weather_data(city, days=5):  # Changed from days=5
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPEN_WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    
    # Extract relevant weather data for the next 'days' days
    weather_data = []
    for item in data['list']:
        date = datetime.fromtimestamp(item['dt'])
        if date.date() <= (datetime.now() + timedelta(days=days)).date():
            weather_data.append({
                'date': date,
                'temperature': item['main']['temp'],
                'wind_speed': item['wind']['speed'],
                'precipitation': item.get('rain', {}).get('3h', 0)  # Precipitation in the last 3 hours
            })
    return weather_data

def calculate_cycling_score(temperature, wind_speed, precipitation):
    temp_score = 0
    wind_score = 0
    precip_score = 0
    
    # Temperature scoring (20% weight)
    if 15 <= temperature <= 25:
        temp_score = 100
    elif 10 <= temperature < 15 or 25 < temperature <= 30:
        temp_score = 70
    elif 5 <= temperature < 10 or 30 < temperature <= 35:
        temp_score = 40
    elif 1 <= temperature < 5:
        temp_score = 0
    else:
        temp_score = -10
    
    # Wind scoring (25% weight)
    if wind_speed < 5:
        wind_score = 100
    elif wind_speed < 10:
        wind_score = 75
    elif wind_speed < 15:
        wind_score = 50
    else:
        wind_score = 25
    
    # Precipitation scoring (45% weight)
    if precipitation == 0:
        precip_score = 100
    elif precipitation < 1:
        precip_score = 75
    elif precipitation < 3:
        precip_score = 40
    else:
        precip_score = 10
    
    # Calculate final weighted score
    final_score = (temp_score * 0.2) + (wind_score * 0.35) + (precip_score * 0.45)
    return round(final_score)

def get_score_emoji(score):
    if score >= 80:
        return "🟢"
    elif score >= 60:
        return "🟡"
    elif score >= 40:
        return "🟠"
    else:
        return "🔴"

# Function to determine the best day for cycling
def find_best_day(weather_data):
    # Group data by date and calculate average scores
    daily_scores = {}
    for item in weather_data:
        date_key = item['date'].date()
        if date_key not in daily_scores:
            daily_scores[date_key] = {
                'count': 0,
                'total_score': 0,
                'data': item
            }
        
        score = calculate_cycling_score(
            item['temperature'], 
            item['wind_speed'], 
            item['precipitation']
        )
        
        daily_scores[date_key]['count'] += 1
        daily_scores[date_key]['total_score'] += score

    # Find the day with highest average score
    best_day = None
    best_score = float('-inf')
    
    for date, data in daily_scores.items():
        avg_score = data['total_score'] / data['count']
        if avg_score > best_score:
            best_score = avg_score
            best_day = data['data']
            
    return best_day

def display_weather_forecast(weather_data, city):
    st.markdown(f"#### {city}")
    
    # Group data by date
    daily_weather = {}
    for item in weather_data:
        date_key = item['date'].date()
        if date_key not in daily_weather:
            daily_weather[date_key] = item
    
    # Display data for each day
    for date, data in sorted(daily_weather.items())[:5]:
        score = calculate_cycling_score(data['temperature'], data['wind_speed'], data['precipitation'])
        score_emoji = get_score_emoji(score)
        
        with st.expander(f"{date.strftime('%A, %B %d')} - Cycling Score: {score} {score_emoji}", expanded=True):
            st.write(f"🌡️ Temperature: {data['temperature']:.1f}°C")
            st.write(f"💨 Wind Speed: {data['wind_speed']:.1f} m/s")
            st.write(f"🌧️ Precipitation: {data['precipitation']:.1f} mm")
            st.progress(score/100)

# Streamlit app
def main():
    st.set_page_config(page_icon=":bike:", layout="centered")
    st.title("Best Day for Cycling 🚴‍♂️")
    st.html("""
        <style>
            .stMainBlockContainer {
                max-width:23rem;
            }
        </style>
        """
    )
    
    city = st.text_input("Enter your city:", "Four Marks, East Hampshire")
    
    if st.button("Get Weather Forecast"):
        # Fetch weather data
        weather_data = get_weather_data(city)
        
        if weather_data:
                        # Find and display the best day for cycling
            best_day = find_best_day(weather_data)
            
            if best_day:
                st.success(f"🎯 Recommended day: {best_day['date'].strftime('%A, %B %d')}")
            else:
                st.warning("No suitable day found in the next 5 days.")
                
            # Display 5-day forecast
            display_weather_forecast(weather_data, city)
            

        else:
            st.error("Failed to fetch weather data. Please check the city name or try again later.")

if __name__ == "__main__":
    main()