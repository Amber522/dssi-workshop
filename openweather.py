import streamlit as st
import requests
from datetime import datetime , timedelta
#from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import time 

# INSERT YOUR API  KEY WHICH YOU PASTED IN YOUR secrets.toml file 
api_key =  st.secrets["api_key"]["key"]
# Endpoint URLs
url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
url_forecast = 'https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}'

# Function to fetch current weather data
def get_weather(city):
    try:
        response = requests.get(url.format(city, api_key))
        if response.status_code == 200:
            json_data = response.json()
            country = json_data['sys']['country']
            temp = json_data['main']['temp'] - 273.15
            temp_feels = json_data['main']['feels_like'] - 273.15
            humid = json_data['main']['humidity']
            icon = json_data['weather'][0]['icon']
            lon = json_data['coord']['lon']
            lat = json_data['coord']['lat']
            des = json_data['weather'][0]['description']
            return [country, round(temp, 1), round(temp_feels, 1), humid, lon, lat, icon, des], json_data
        else:
            st.error("Error in fetching current weather data.")
            return None, None
    except requests.RequestException as e:
        st.error(f"Error occurred: {e}")
        return None, None

# Function to fetch forecast data
def get_forecast_data(lat, lon):
    try:
        response = requests.get(url_forecast.format(lat, lon, api_key))
        if response.status_code == 200:
            data = response.json()
            forecasts = []
            for forecast in data['list']:
                timestamp = forecast['dt']
                date_time = datetime.fromtimestamp(timestamp)
                temperature = forecast['main']['temp'] - 273.15
                weather_description = forecast['weather'][0]['description']
                forecasts.append({
                    'DateTime': date_time,
                    'Temperature (°C)': temperature,
                    'Description': weather_description
                })
            return forecasts
        else:
            st.error(f"Error fetching forecast data. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        st.error(f"Request failed: {e}")
        return None

# Streamlit application
st.header('Streamlit Weather Report')
st.balloons()
st.markdown('https://openweathermap.org/api')

# Load images
im1, im2 = st.columns(2)
with im2:
    st.image('random4.jpg', use_column_width=True, caption='Somewhere in Singapore.')
with im1:
    st.image('OPENWEATHER.png', caption='Open Weather Map API as our Data Resource.', use_column_width=True)

# Input and fetch current weather
col1, col2 = st.columns(2)
with col1:
    city_name = st.text_input("Enter city name", "Singapore")

with col2:
    if city_name:
        res, json_data = get_weather(city_name)

        if res and json_data:
            st.success(f'Current Temperature: {round(res[1], 2)}°C')
            st.info(f'Feels Like: {round(res[2], 2)}°C')
            st.info(f'Humidity: {res[3]}%')
            st.subheader(f'Weather Status: {res[7].capitalize()}')
            weather_icon_url = f"http://openweathermap.org/img/wn/{res[6]}@2x.png"
            st.image(weather_icon_url)

# Display forecast data
if city_name:
    show_forecast = st.expander(label='Next 5 Days Forecast')
    with show_forecast:
        start_date_string = st.date_input('Select Date')
        if start_date_string:
            forecast_data = get_forecast_data(res[5], res[4])

            if forecast_data:
                df = pd.DataFrame(forecast_data)
                st.write(df)
            else:
                st.warning("No forecast data available.")

# Display map with current city coordinates
if res:
    st.map(pd.DataFrame({'lat': [res[5]], 'lon': [res[4]]}, columns=['lat', 'lon']))
