from view_model import create_gui
from process_data import display_weather_info

def main():
    root, city_entry, weather_text = create_gui(display_weather_info)
    root.mainloop()

if __name__ == "__main__":
    main()