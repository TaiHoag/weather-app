import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as tk
import sqlalchemy as db
import openmeteo_requests
import requests_cache
from retry_requests import retry
from datetime import datetime
import pytz


# API Calls
def fetch_weather_data(latitude, longitude):
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "rain",
            "cloud_cover",
        ],
        "daily": "uv_index_max",
        "timezone": "auto",
        "past_days": 3,
    }
    response = openmeteo.weather_api(url, params=params)
    return response[0]


# Get City Data
def get_city_coordinates(city_name):
    try:
        city_data = pd.read_excel(
            "worldcities/worldcities.xlsx", usecols=["city", "lat", "lng"]
        )
        city_info = city_data[city_data["city"] == city_name]
        if not city_info.empty:
            latitude, longitude = city_info.iloc[0][["lat", "lng"]]
            return latitude, longitude
        else:
            print("City not found in database.")
            return None, None
    except FileNotFoundError:
        print("City coordinates file not found.")
        return None, None


def get_all_city_names():
    df = pd.read_excel("worldcities/worldcities.xlsx", usecols=["city"])
    return df["city"].tolist()


# Data Processing
def process_hourly_data(response, city_name):
    hourly = response.Hourly()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        ),
        "city_name": city_name,
        "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
        "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
        "precipitation": hourly.Variables(2).ValuesAsNumpy(),
        "rain": hourly.Variables(3).ValuesAsNumpy(),
        "cloud_cover": hourly.Variables(4).ValuesAsNumpy(),
    }
    return pd.DataFrame(data=hourly_data)


def process_daily_data(response, city_name):
    daily = response.Daily()
    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left",
        ),
        "city_name": city_name,
        "uv_index_max": daily.Variables(0).ValuesAsNumpy(),
    }
    return pd.DataFrame(data=daily_data)


# Store Data
def store_hourly_data(hourly_dataframe):
    engine = db.create_engine("sqlite:///weather_data.db")
    hourly_dataframe.to_sql(
        "hourly_data",
        con=engine,
        if_exists="append",
        index=False)


def store_daily_data(daily_dataframe):
    engine = db.create_engine("sqlite:///weather_data.db")
    daily_dataframe.to_sql(
        "daily_data",
        con=engine,
        if_exists="append",
        index=False)


# Analysis Functions
def analyze_data(data, column):
    mean_val = data[column].mean()
    median_val = data[column].median()
    max_val = data[column].max()
    min_val = data[column].min()
    std_val = data[column].std()
    range_val = max_val - min_val
    q1 = data[column].quantile(0.25)
    q3 = data[column].quantile(0.75)
    iqr = q3 - q1

    peaks = data[data[column] > (mean_val + std_val)]
    troughs = data[data[column] < (mean_val - std_val)]

    analysis_report = f"""
    Analysis for {column.replace('_', ' ').title()}:
    - Mean: {mean_val:.2f}
    - Median: {median_val:.2f}
    - Max: {max_val:.2f}
    - Min: {min_val:.2f}
    - Std Dev: {std_val:.2f}
    - Range: {range_val:.2f}
    - Interquartile Range (IQR): {iqr:.2f}
    - Number of Peaks: {len(peaks)}
    - Number of Troughs: {len(troughs)}
    """
    return analysis_report


def generate_weather_description(hourly_dataframe):
    descriptions = []
    temp_mean = hourly_dataframe["temperature_2m"].mean()
    humidity_mean = hourly_dataframe["relative_humidity_2m"].mean()
    precip_sum = hourly_dataframe["precipitation"].sum()
    cloud_cover_mean = hourly_dataframe["cloud_cover"].mean()

    descriptions.append(
        f"The average temperature over the past hours was {temp_mean:.2f}°C.")
    descriptions.append(
        f"Average relative humidity was around {humidity_mean:.2f}%.")
    if precip_sum > 0:
        descriptions.append(
            f"There was a total of {precip_sum:.2f} mm of precipitation.")
    else:
        descriptions.append("No precipitation was recorded.")
    descriptions.append(f"Average cloud cover was {cloud_cover_mean:.2f}%.")

    if temp_mean > 30:
        descriptions.append("It has been quite hot.")
    elif temp_mean < 10:
        descriptions.append("It has been quite cold.")
    if humidity_mean > 70:
        descriptions.append("Humidity has been high.")
    if cloud_cover_mean > 70:
        descriptions.append("It has been mostly cloudy.")

    return "\n".join(descriptions)


# Calculate Local Time of City
def get_local_time(response):
    timezone = response.Timezone()
    local_time = datetime.now(pytz.timezone(timezone))
    return local_time


# Plotting Functions
def plot_in_new_window(data, title, xlabel, ylabel, local_time):
    new_window = tk.CTkToplevel()
    new_window.title(title)
    new_window._state_before_windows_set_titlebar_color = "zoomed"
    fig, ax = plt.subplots(figsize=(10, 6))

    plot_color, fg_color, bg_color = get_color_gradient(local_time.hour)

    fig.patch.set_facecolor(bg_color)
    ax.plot(
        data["date"],
        data[ylabel],
        marker="o",
        linestyle="-",
        color=plot_color)
    ax.set_title(title, color=plot_color)
    ax.set_xlabel(xlabel, color=plot_color)
    ax.set_ylabel(ylabel, color=plot_color)
    ax.set_facecolor(fg_color)
    ax.tick_params(axis="x", rotation=45, colors=plot_color)
    ax.tick_params(axis="y", colors=plot_color)
    ax.grid(True, color=plot_color)

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, new_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    analysis_report = analyze_data(data, ylabel)

    text_box = tk.CTkTextbox(
        new_window,
        width=100,
        height=100,
        font=("Calibri", 20))
    text_box.insert(tk.END, analysis_report)
    text_box.configure(state="disabled")
    text_box.pack(fill=tk.BOTH, expand=True)


def get_sky_color(time_of_day):
    if 6 <= time_of_day < 12:
        return "whitesmoke"
    elif 12 <= time_of_day < 18:
        return "bisque"
    elif 18 <= time_of_day < 20:
        return "lightpink"
    else:
        return "royalblue"


def get_color_gradient(time_of_day):
    if 6 <= time_of_day < 12:
        plot_color = "whitesmoke"
        fg_color = "deepskyblue"
        bg_color = "deepskyblue"
    elif 12 <= time_of_day < 18:
        plot_color = "bisque"
        fg_color = "coral"
        bg_color = "coral"
    elif 18 <= time_of_day < 20:
        plot_color = "lightpink"
        fg_color = "slateblue"
        bg_color = "slateblue"
    else:
        plot_color = "royalblue"
        fg_color = "black"
        bg_color = "black"
    return plot_color, fg_color, bg_color


def visualize_hourly_weather(hourly_dataframe, canvas, local_time):
    fig, axs = plt.subplots(3, 2, figsize=(12, 8))

    plot_color, fg_color, bg_color = get_color_gradient(local_time.hour)

    fig.patch.set_facecolor(bg_color)
    axs[0, 0].plot(
        hourly_dataframe["date"],
        hourly_dataframe["temperature_2m"],
        marker="o",
        linestyle="-",
        color=plot_color,
    )
    axs[0, 0].set_title("Hourly Temperature Variation", color=plot_color)
    axs[0, 0].set_xlabel("Date", color=plot_color)
    axs[0, 0].set_ylabel("Temperature (°C)", color=plot_color)
    axs[0, 0].set_facecolor(fg_color)
    axs[0, 0].tick_params(axis="x", rotation=45, colors=plot_color)
    axs[0, 0].tick_params(axis="y", colors=plot_color)
    axs[0, 0].grid(True, color=plot_color)

    axs[0, 1].plot(
        hourly_dataframe["date"],
        hourly_dataframe["relative_humidity_2m"],
        marker="o",
        linestyle="-",
        color=plot_color,
    )
    axs[0, 1].set_title("Hourly Humidity Variation", color=plot_color)
    axs[0, 1].set_xlabel("Date", color=plot_color)
    axs[0, 1].set_ylabel("Relative Humidity (%)", color=plot_color)
    axs[0, 1].set_facecolor(fg_color)
    axs[0, 1].tick_params(axis="x", rotation=45, colors=plot_color)
    axs[0, 1].tick_params(axis="y", colors=plot_color)
    axs[0, 1].grid(True, color=plot_color)

    axs[1, 0].plot(
        hourly_dataframe["date"],
        hourly_dataframe["precipitation"],
        marker="o",
        linestyle="-",
        color=plot_color,
    )
    axs[1, 0].set_title("Hourly Precipitation Variation", color=plot_color)
    axs[1, 0].set_xlabel("Date", color=plot_color)
    axs[1, 0].set_ylabel("Precipitation (mm)", color=plot_color)
    axs[1, 0].set_facecolor(fg_color)
    axs[1, 0].tick_params(axis="x", rotation=45, colors=plot_color)
    axs[1, 0].tick_params(axis="y", colors=plot_color)
    axs[1, 0].grid(True, color=plot_color)

    axs[1, 1].plot(
        hourly_dataframe["date"],
        hourly_dataframe["rain"],
        marker="o",
        linestyle="-",
        color=plot_color,
    )
    axs[1, 1].set_title("Hourly Rain Variation", color=plot_color)
    axs[1, 1].set_xlabel("Date", color=plot_color)
    axs[1, 1].set_ylabel("Rain (mm)", color=plot_color)
    axs[1, 1].set_facecolor(fg_color)
    axs[1, 1].tick_params(axis="x", rotation=45, colors=plot_color)
    axs[1, 1].tick_params(axis="y", colors=plot_color)
    axs[1, 1].grid(True, color=plot_color)

    axs[2, 0].plot(
        hourly_dataframe["date"],
        hourly_dataframe["cloud_cover"],
        marker="o",
        linestyle="-",
        color=plot_color,
    )
    axs[2, 0].set_title("Hourly Cloud Cover Variation", color=plot_color)
    axs[2, 0].set_xlabel("Date", color=plot_color)
    axs[2, 0].set_ylabel("Cloud Cover (%)", color=plot_color)
    axs[2, 0].set_facecolor(fg_color)
    axs[2, 0].tick_params(axis="x", rotation=45, colors=plot_color)
    axs[2, 0].tick_params(axis="y", colors=plot_color)
    axs[2, 0].grid(True, color=plot_color)

    axs[2, 1].axis("off")

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, canvas)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def on_click(event, ax, title, ylabel):
        if event.inaxes == ax:
            plot_in_new_window(
                hourly_dataframe,
                title,
                "Date",
                ylabel,
                local_time)

    fig.canvas.mpl_connect(
        "button_press_event",
        lambda event: on_click(
            event, axs[0, 0], "Hourly Temperature Variation", "temperature_2m"
        ),
    )
    fig.canvas.mpl_connect(
        "button_press_event",
        lambda event: on_click(
            event, axs[0, 1], "Hourly Humidity Variation", "relative_humidity_2m"
        ),
    )
    fig.canvas.mpl_connect(
        "button_press_event",
        lambda event: on_click(
            event, axs[1, 0], "Hourly Precipitation Variation", "precipitation"
        ),
    )
    fig.canvas.mpl_connect(
        "button_press_event",
        lambda event: on_click(
            event, axs[1, 1], "Hourly Rain Variation", "rain"
        ),
    )
    fig.canvas.mpl_connect(
        "button_press_event",
        lambda event: on_click(
            event, axs[2, 0], "Hourly Cloud Cover Variation", "cloud_cover"
        ),
    )

# Display Data


def display_weather_info(city_entry, weather_text, description_text, canvas):
    city_name = city_entry.get()
    latitude, longitude = get_city_coordinates(city_name)
    if latitude is None or longitude is None:
        return

    response = fetch_weather_data(latitude, longitude)
    local_time = get_local_time(response)

    weather_text.configure(state="normal")
    weather_text.delete(1.0, tk.END)
    weather_text.insert(tk.END, f"City Name: {city_name}\n")
    weather_text.insert(tk.END, f"Coordinates: {latitude}°N, {longitude}°E\n")
    weather_text.insert(tk.END, f"Elevation: {response.Elevation()} m asl\n")
    weather_text.insert(
        tk.END,
        f"Timezone: {response.Timezone()} {response.TimezoneAbbreviation()}\n")
    weather_text.configure(state="disabled")

    hourly_dataframe = process_hourly_data(response, city_name)
    daily_dataframe = process_daily_data(response, city_name)

    store_hourly_data(hourly_dataframe)
    store_daily_data(daily_dataframe)
    visualize_hourly_weather(hourly_dataframe, canvas, local_time)

    weather_description = generate_weather_description(hourly_dataframe)
    description_text.configure(state="normal")
    description_text.delete(1.0, tk.END)
    description_text.insert(tk.END, weather_description)
    description_text.configure(state="disabled")

# GUI


def create_gui(fetch_weather_callback):
    root = tk.CTk()
    root.title("Weather App")
    root._state_before_windows_set_titlebar_color = "zoomed"

    current_hour = datetime.now().hour
    sky_color = get_sky_color(current_hour)
    root.configure(bg=sky_color)

    myfont = tk.CTkFont(family="Calibri", size=20)

    city_names = get_all_city_names()

    combobox_var = tk.StringVar(value="")
    city_entry = tk.CTkComboBox(
        root,
        width=250,
        values=city_names,
        variable=combobox_var)
    city_entry.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

    def checkkey(event):
        value = city_entry.get()
        city_list = [city for city in city_names if city.lower(
        ).startswith(value.lower())][:5]
        update_suggestions(city_list)

    def update_suggestions(city_list):
        if city_list:
            city_entry.configure(values=city_list)
        else:
            city_entry.configure(values=(""))

    city_entry.bind("<KeyRelease>", checkkey)

    fetch_button = tk.CTkButton(
        root,
        font=myfont,
        text="Fetch Weather",
        fg_color="orange",
        hover_color="#ff6100",
        command=fetch_weather_callback,
    )
    fetch_button.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

    weather_text = tk.CTkTextbox(
        root,
        font=myfont,
        width=200,
        height=150,
        scrollbar_button_color="orange",
        corner_radius=16,
        border_color="orange",
        border_width=2,
    )
    weather_text.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

    description_text = tk.CTkTextbox(
        root,
        font=myfont,
        width=200,
        height=150,
        scrollbar_button_color="orange",
        corner_radius=16,
        border_color="orange",
        border_width=2,
    )
    description_text.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")

    canvas_frame = tk.CTkFrame(root, width=800, height=600)
    canvas_frame.grid(
        row=2,
        column=1,
        columnspan=2,
        padx=5,
        pady=5,
        sticky="nsew")

    root.grid_rowconfigure(2, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)

    root.bind("<Escape>", lambda event: root.destroy())

    return root, city_entry, weather_text, description_text, canvas_frame

# Main


def main():
    root, city_entry, weather_text, description_text, canvas_frame = create_gui(
        lambda: display_weather_info(
            city_entry, weather_text, description_text, canvas_frame))
    root.mainloop()


if __name__ == "__main__":
    main()
