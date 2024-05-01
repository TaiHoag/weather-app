import pandas as pd
import matplotlib.pyplot as plt

def visualize_hourly_temperature(hourly_dataframe):
    plt.figure(figsize=(10, 6))
    plt.plot(hourly_dataframe['date'], hourly_dataframe['temperature_2m'], marker='o', linestyle='-')
    plt.title('Hourly Temperature Variation')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
