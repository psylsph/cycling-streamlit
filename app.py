import streamlit as st

st.set_page_config(page_title="Cycling Weather", layout="wide")

st.title("Rayne")

def display_weather_card(day, date, time_range, temp_high, temp_low, conditions, wind, uv, hourly_temps=None, rain_chance=None):
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
            else:
                st.markdown(f"<h1 style='text-align: center; color: green;'>{temp_high}</h1>", unsafe_allow_html=True)
            if hourly_temps:
                for time, temp in hourly_temps.items():
                    if temp > 60:
                        st.markdown(f"<p style='text-align: center; color: green;'>{time} {temp}</p>", unsafe_allow_html=True)
                    elif temp < 0:
                        st.markdown(f"<p style='text-align: center; color: red;'>{time} {temp}</p>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<p style='text-align: center;'>{time} {temp}</p>", unsafe_allow_html=True)

        with col3:
            st.write(f"{wind}")
            st.write(f"UV {uv}")
            if rain_chance:
                st.write(f"{rain_chance}")

        st.markdown("---")


display_weather_card(
    day="Thu",
    date="Jan 2",
    time_range="8:04 AM  3:58 PM",
    temp_high="NaN",
    temp_low="2",
    conditions="Clear Sky",
    wind="15 m/s",
    uv="Low",
)

display_weather_card(
    day="Fri",
    date="Jan 3",
    time_range="8:04 AM  3:58 PM",
    temp_high="62",
    temp_low="-1",
    conditions="Clear Sky",
    wind="15 m/s",
    uv="Low",
    hourly_temps={"9:00 AM": 54, "12:00 PM": 61, "3:00 PM": 70},
)

display_weather_card(
    day="Sat",
    date="Jan 4",
    time_range="8:04 AM  3:58 PM",
    temp_high="42",
    temp_low="0",
    conditions="Broken Clouds",
    wind="7 m/s",
    uv="Low",
    hourly_temps={"9:00 AM": 67, "12:00 PM": 58, "3:00 PM": 0},
    rain_chance="100%"
)
