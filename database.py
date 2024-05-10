import pandas as pd
import sqlalchemy as db

def store_hourly_data(hourly_dataframe):
    engine = db.create_engine('sqlite:///weather_data.db')
    connection = engine.connect()
    metadata = db.MetaData()

    hourly_dataframe.to_sql('hourly_data', con=engine, if_exists='append', index=False)

def store_daily_data(daily_dataframe):
    engine = db.create_engine('sqlite:///weather_data.db')
    connection = engine.connect()
    metadata = db.MetaData()

    daily_dataframe.to_sql('daily_data', con=engine, if_exists='append', index=False)
