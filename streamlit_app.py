import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

API_KEY = '72d9310ffacf2a2511dee935ab09733f'


def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        return None

    return {
        "City": data.get("name"),
        "Country": data["sys"].get("country"),
        "Temperature": data["main"].get("temp"),
        "Temp Minimum": data["main"].get("temp_min"),
        "Temp Maximum": data["main"].get("temp_max"),
        "Weather": data["weather"][0]["description"].title(),
        "Humidity": data["main"].get("humidity"),
        "Wind Speed": data["wind"].get("speed"),
        "Sunrise": data["sys"].get("sunrise"),
        "Sunset": data["sys"].get("sunset"),
        "Icon": data["weather"][0]["icon"]
    }


def get_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        return pd.DataFrame(), pd.DataFrame()

    hourly_forecast = []
    for x in data['list'][:8]:
        hourly_forecast.append({
            "Time": pd.to_datetime(x['dt'], unit='s').strftime('%H:%M'),
            "Temperature": x['main']['temp']
        })

    daily_forecast = {}
    for x in data['list']:
        date = pd.to_datetime(x['dt'], unit='s').strftime('%A')
        if date not in daily_forecast:
            daily_forecast[date] = x['main']['temp']

    weekly_forecast = pd.DataFrame(list(daily_forecast.items()), columns=["Day", "Temperature"])

    return pd.DataFrame(hourly_forecast), weekly_forecast


st.title("🌦️ Weather App")
st.write("🔎 Enter a city to get the current weather and forecast.")

city = st.text_input("📍 City", st.session_state.get("selected_city", "Berlin"))

weather_data = get_weather(city)
hourly_forecast, weekly_forecast = get_forecast(city)

if weather_data:
    sunrise_time = pd.to_datetime(weather_data["Sunrise"], unit='s').strftime('%H:%M')
    sunset_time = pd.to_datetime(weather_data["Sunset"], unit='s').strftime('%H:%M')


    def delta():
        return round(weather_data['Temp Maximum'] - weather_data['Temp Minimum'], 2)


    st.subheader(f"🌍 Weather in {weather_data['City']}, {weather_data['Country']}")
    st.write(f"**🌤️ Condition:** {weather_data['Weather']}")

    icon_url = f"http://openweathermap.org/img/wn/{weather_data['Icon']}@2x.png"
    st.image(icon_url, width=100)

    with st.container():
        a, b, c = st.columns(3)
        d, e = st.columns(2)
        a.metric("🌡️ Temperature", f"{weather_data['Temperature']}°C", delta())
        b.metric("💧 Humidity", f"{weather_data['Humidity']}%")
        c.metric("💨 Wind Speed", f"{weather_data['Wind Speed']} m/s")
        d.metric("🌅 Sunrise", sunrise_time)
        e.metric("🌇 Sunset", sunset_time)

    if not hourly_forecast.empty:
        st.subheader("📊 Today's Temperature Forecast (Next 24 Hours)")

        fig_hourly = go.Figure()
        fig_hourly.add_trace(go.Scatter(
            x=hourly_forecast["Time"],
            y=hourly_forecast["Temperature"],
            mode='lines+markers',
            line=dict(shape="spline", smoothing=0.8, color="dodgerblue", width=3),
            marker=dict(size=7, color="blue", opacity=0.7),
            name="Temperature"
        ))

        fig_hourly.update_layout(
            title="Hourly Temperature Changes",
            xaxis_title="Time (Hours)",
            yaxis_title="Temperature (°C)",
            template="plotly_dark",
            xaxis=dict(showgrid=True, gridcolor="gray"),
            yaxis=dict(showgrid=True, gridcolor="gray"),
            font=dict(size=14)
        )

        st.plotly_chart(fig_hourly)

    else:
        st.warning("⚠️ Could not retrieve hourly forecast data. Please check the city name and try again.")

    if not weekly_forecast.empty:
        st.subheader("📆 Weekly Temperature Forecast")

        fig_weekly = go.Figure()
        fig_weekly.add_trace(go.Scatter(
            x=weekly_forecast["Day"],
            y=weekly_forecast["Temperature"],
            mode='lines+markers',
            line=dict(shape="spline", smoothing=0.8, color="orangered", width=3),
            marker=dict(size=8, color="red", opacity=0.8),
            name="Temperature"
        ))

        fig_weekly.update_layout(
            title="Temperature Trend for the Next 7 Days",
            xaxis_title="Day of the Week",
            yaxis_title="Temperature (°C)",
            template="plotly_dark",
            xaxis=dict(showgrid=True, gridcolor="gray"),
            yaxis=dict(showgrid=True, gridcolor="gray"),
            font=dict(size=14)
        )

        st.plotly_chart(fig_weekly)

    else:
        st.warning("THAT CITY DOESN'T EXIST")

else:
    st.warning("THAT CITY DOESN'T EXIST")
