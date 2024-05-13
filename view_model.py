import customtkinter as tk
from city_input import get_all_city_names
from CTkListbox import *

def on_key_press(event, city_entry, city_names, city_listbox):
    input_text = city_entry.get()
    suggestions = [city for city in city_names if city.startswith(input_text)][:5]  # Limit to 5 suggestions
    city_listbox.delete(0, tk.END)
    for word in suggestions:
        city_listbox.insert(tk.END, word)

def on_suggestion_select(city_entry, city_listbox):
    selected_index = city_listbox.curselection()
    if selected_index:
        selected_word = city_listbox.get(selected_index)
        city_entry.delete(0, tk.END)
        city_entry.insert(tk.END, selected_word)

def create_gui(fetch_weather_callback):
    root = tk.CTk()
    root.title("Weather App")
    root.geometry("500x500")
    myfont = tk.CTkFont(family="Calibri", size=20)

    city_names = get_all_city_names()

    city_entry = tk.CTkEntry(root, font=myfont, width=250)
    city_entry.grid(row=0, column=1, padx=5, pady=5)

    city_listbox = CTkListbox(root, font=myfont, width=250)
    city_listbox.grid(row=1, column=1, padx=5, pady=5)

    city_entry.bind("<KeyRelease>", lambda event, entry=city_entry, names=city_names, listbox=city_listbox: on_key_press(event, entry, names, listbox))
    city_listbox.bind("<Double-Button-1>", lambda event, entry=city_entry, listbox=city_listbox: on_suggestion_select(entry, listbox))

    fetch_button = tk.CTkButton(root, font=myfont, text="Fetch Weather", fg_color="orange", hover_color="#ff6100", command=fetch_weather_callback)
    fetch_button.grid(row=0, column=2, padx=5, pady=5)

    weather_text = tk.CTkTextbox(root, font=myfont, width=400, scrollbar_button_color="Orange", corner_radius=16, border_color="Orange", border_width=2)
    weather_text.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

    return root, city_entry, weather_text, city_listbox
