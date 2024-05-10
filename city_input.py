import pandas as pd

def get_city_coordinates(city_name):
    # Load city coordinates from Excel file
    try:
        city_data = pd.read_excel("worldcities\worldcities.xlsx")
        city_info = city_data[city_data['city'] == city_name]
        if not city_info.empty:
            latitude = city_info.iloc[0]['lat']
            longitude = city_info.iloc[0]['lng']
            return latitude, longitude
        else:
            print("City not found in database.")
            return None, None
    except FileNotFoundError:
        print("City coordinates file not found.")
        return None, None

# Function to fetch city names from the file
def get_all_city_names():
    df = pd.read_excel("worldcities\worldcities.xlsx")
    return df['city'].tolist()