import customtkinter as tk
from city_input import get_all_city_names
from CTkListbox import *

def create_gui(fetch_weather_callback):
    root = tk.CTk()
    root.title("Weather App")
    root.geometry("1080x1080")
    myfont = tk.CTkFont(family="Calibri", size=20)

    city_names = get_all_city_names()

    combobox_var = tk.StringVar(value="")
    city_entry = tk.CTkComboBox(root, width = 250, values=city_names, variable=combobox_var)
    city_entry.grid(row=0, column=1, padx=5, pady=5)

    def checkkey(event):
        value = city_entry.get()
        city_list = city_names

        city_list = [city for city in city_list if city.lower().startswith(value.lower())][:5]
        
        update_suggestions(city_list)
        
    
    def update_suggestions(city_list):
        
        if city_list:
            city_entry.configure(values=city_list)
        else:
            city_entry.configure(values=(""))    

    city_entry.bind('<KeyRelease>', checkkey)

    fetch_button = tk.CTkButton(root, font=myfont, text="Fetch Weather", fg_color="orange", hover_color="#ff6100", command=fetch_weather_callback)
    fetch_button.grid(row=0, column=2, padx=5, pady=5)

    weather_text = tk.CTkTextbox(root, font=myfont, width=400, scrollbar_button_color="Orange", corner_radius=16, border_color="Orange", border_width=2)
    weather_text.grid(row=3, column=1, padx=5, pady=5)

    return root, city_entry, weather_text