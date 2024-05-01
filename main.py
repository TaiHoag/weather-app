from api_call import fetch_weather_data
from database import store_hourly_data, store_daily_data
from visualization import visualize_hourly_temperature
import pandas as pd

def main():
    # Fetch weather data
    response = fetch_weather_data()

    # Process hourly data
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
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["rain"] = hourly_rain
    hourly_data["cloud_cover"] = hourly_cloud_cover

    hourly_dataframe = pd.DataFrame(data=hourly_data)

    # Store hourly data in the database
    store_hourly_data(hourly_dataframe)

    # Process daily data
    daily = response.Daily()
    daily_uv_index_max = daily.Variables(0).ValuesAsNumpy()

    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )
    }
    daily_data["uv_index_max"] = daily_uv_index_max

    daily_dataframe = pd.DataFrame(data=daily_data)

    # Store daily data in the database
    store_daily_data(daily_dataframe)

    # Visualize hourly temperature
    visualize_hourly_temperature(hourly_dataframe)

if __name__ == "__main__":
    main()
