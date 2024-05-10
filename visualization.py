import pandas as pd
import matplotlib.pyplot as plt

def visualize_hourly_weather(hourly_dataframe):
    plt.figure(figsize=(10, 6))

    # Plot temperature
    plt.subplot(2, 2, 1)
    plt.plot(hourly_dataframe['date'], hourly_dataframe['temperature_2m'], marker='o', linestyle='-')
    plt.title('Hourly Temperature Variation')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.xticks(rotation=45)
    plt.grid(True)

    # Plot humidity
    plt.subplot(2, 2, 2)
    plt.plot(hourly_dataframe['date'], hourly_dataframe['relative_humidity_2m'], marker='o', linestyle='-')
    plt.title('Hourly Humidity Variation')
    plt.xlabel('Date')
    plt.ylabel('Relative Humidity (%)')
    plt.xticks(rotation=45)
    plt.grid(True)

    # Plot precipitation
    plt.subplot(2, 2, 3)
    plt.plot(hourly_dataframe['date'], hourly_dataframe['precipitation'], marker='o', linestyle='-')
    plt.title('Hourly Precipitation Variation')
    plt.xlabel('Date')
    plt.ylabel('Precipitation (mm)')
    plt.xticks(rotation=45)
    plt.grid(True)

    # Plot rain
    plt.subplot(2, 2, 4)
    plt.plot(hourly_dataframe['date'], hourly_dataframe['rain'], marker='o', linestyle='-')
    plt.title('Hourly Rain Variation')
    plt.xlabel('Date')
    plt.ylabel('Rain (mm)')
    plt.xticks(rotation=45)
    plt.grid(True)

    plt.tight_layout()
    plt.show()
