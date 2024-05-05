
import tkinter as tk
import pandas as pd
from tkinter import messagebox
from weather_api import fetch_weather_data
from database import store_hourly_data, store_daily_data
from visualization import visualize_hourly_temperature
from city_input import get_city_coordinates

def display_weather_info():
    city_name = city_entry.get()  # Retrieve the value from the Entry widget
    latitude, longitude = get_city_coordinates(city_name)
    if latitude is None or longitude is None:
        return

    # Fetch weather data
    response = fetch_weather_data(latitude, longitude)

    # Display weather information in the text widget
    weather_text.delete(1.0, tk.END) # Clear previous fetch result
    weather_text.insert(tk.END, f"City Name {city_name}\n")
    weather_text.insert(tk.END, f"Coordinates: {latitude}°N, {longitude}°E\n\n")
    weather_text.insert(tk.END, f"Elevation: {response.Elevation()} m asl\n")
    weather_text.insert(tk.END, f"Timezone: {response.Timezone()} {response.TimezoneAbbreviation()}\n")
    weather_text.insert(tk.END, f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()} s\n\n")

    hourly_dataframe = process_hourly_data(response)
    daily_dataframe = process_daily_data(response)

    # Store data in the database
    store_hourly_data(hourly_dataframe)
    store_daily_data(daily_dataframe)

    # Visualize hourly temperature
    visualize_hourly_temperature(hourly_dataframe)

def process_hourly_data(response):
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
    hourly_rain = hourly.Variables(3).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(4).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )
    }
    hourly_data["city_name"] = city_entry.get()
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["rain"] = hourly_rain
    hourly_data["cloud_cover"] = hourly_cloud_cover

    return pd.DataFrame(data=hourly_data)

def process_daily_data(response):
    daily = response.Daily()
    daily_uv_index_max = daily.Variables(0).ValuesAsNumpy()
    city_name = city_entry.get()


    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )
    }
    daily_data["city_name"] = city_name
    daily_data["uv_index_max"] = daily_uv_index_max

    return pd.DataFrame(data=daily_data)

# Create the main window
root = tk.Tk()
root.title("Weather App")

# Create GUI components
city_label = tk.Label(root, text="Enter city name:")
city_label.grid(row=0, column=0)

city_entry = tk.Entry(root)
city_entry.grid(row=0, column=1)

fetch_button = tk.Button(root, text="Fetch Weather", command=display_weather_info)
fetch_button.grid(row=0, column=2)

weather_text = tk.Text(root, height=10, width=50)
weather_text.grid(row=1, columnspan=3)

root.mainloop()