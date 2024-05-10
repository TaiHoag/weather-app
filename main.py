import customtkinter as tk
import pandas as pd
from weather_api import fetch_weather_data
from database import store_hourly_data, store_daily_data
from visualization import visualize_hourly_weather
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
    weather_text.insert(tk.END, f"City Name: {city_name}\n")
    weather_text.insert(tk.END, f"Coordinates: {latitude}°N, {longitude}°E\n\n")
    weather_text.insert(tk.END, f"Elevation: {response.Elevation()} m asl\n")
    weather_text.insert(tk.END, f"Timezone: {response.Timezone()} {response.TimezoneAbbreviation()}\n")

    hourly_dataframe = process_hourly_data(response)
    daily_dataframe = process_daily_data(response)

    # Store data in the database
    store_hourly_data(hourly_dataframe)
    store_daily_data(daily_dataframe)

    # Visualize hourly temperature
    visualize_hourly_weather(hourly_dataframe)

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
root = tk.CTk()
root.title("Weather App")
root.geometry("500x500")
myfont = tk.CTkFont(family="Calibri", size=15)

# Create GUI components
city_entry = tk.CTkEntry(root, font=myfont, placeholder_text="Type a City name ...", width=200)
city_entry.grid(row=0, column=1, padx=5, pady=5)

fetch_button = tk.CTkButton(root, font=myfont, text="Fetch Weather", fg_color="orange", hover_color="#ff6100", command=display_weather_info)
fetch_button.grid(row=0, column=2, padx=5, pady=5)

weather_text = tk.CTkTextbox(root, font=myfont, width=400, scrollbar_button_color="Orange", corner_radius=16, border_color="Orange", border_width=2)
weather_text.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

root.mainloop()
