import customtkinter as tk
from city_input import get_all_city_names

def create_gui(fetch_weather_callback):
    root = tk.CTk()
    root.title("Weather App")
    root.geometry("500x500")
    myfont = tk.CTkFont(family="Calibri", size=20)

    city_names = get_all_city_names()

    city_entry = tk.CTkComboBox(root, values=city_names, font=myfont, width=250)
    city_entry.grid(row=0, column=1, padx=5, pady=5)

    fetch_button = tk.CTkButton(root, font=myfont, text="Fetch Weather", fg_color="orange", hover_color="#ff6100", command=lambda: fetch_weather_callback(city_entry, weather_text))
    fetch_button.grid(row=0, column=2, padx=5, pady=5)

    weather_text = tk.CTkTextbox(root, font=myfont, width=400, scrollbar_button_color="Orange", corner_radius=16, border_color="Orange", border_width=2)
    weather_text.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    return root, city_entry, weather_text