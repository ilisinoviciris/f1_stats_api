import fastf1
import pandas as pd
from pathlib import Path
from app import database, models
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# enable cache directory
cache_dir = Path("data/fastf1_cache")
cache_dir.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

# session mapping between FastF1 and OpenF1 for differently named practice sessions (Practice 1/2/3 vs. FP1/2/3)
SESSION_MAPPING = {
    "Practice 1": "FP1",
    "Practice 2": "FP2",
    "Practice 3": "FP3",
    "Qualifying": "Qualifying",
    "Race": "Race",
    "Sprint": "Sprint",
    "Sprint Shootout": "Sprint Shootout",  # for 2023 season
    "Sprint Qualifying": "Sprint Qualifying"  # for 2024 and 2025 season
}

# aggregate weather for one session
def aggregate_session_weather(weather_data: pd.DataFrame) -> dict:
    """
    Aggregates session-level weather metrics from FastF1 Weather data:
    - air_temp: average air temperature (°C)
    - humidity: average relative humidity (%)
    - pressure: average air pressure (mbar)
    - rainfall: True if rainfall occurred during the session
    - track_temp: average track temperature (°C)
    - wind_direction: average wind direction (°)
    - wind_speed: average wind speed (m/s)
    """
    # if there's no weather data for that session return empty
    if weather_data is None or weather_data.empty:
        return {}

    df = weather_data

    # safe access for columns
    has_air_temp = "AirTemp" in df.columns
    has_humidity = "Humidity" in df.columns
    has_pressure = "Pressure" in df.columns
    has_rainfall = "Rainfall" in df.columns
    has_track_temp = "TrackTemp" in df.columns
    has_wind_direction = "WindDirection" in df.columns
    has_wind_speed = "WindSpeed" in df.columns

    return {
        "air_temp": float(df["AirTemp"].mean()) if has_air_temp else None,
        "humidity": float(df["Humidity"].mean()) if has_humidity else None,
        "pressure": float(df["Pressure"].mean()) if has_pressure else None,      
        # True if any rainfall occurred during the session
        "rainfall": bool(df["Rainfall"].any()) if has_rainfall else None,
        "track_temp": float(df["TrackTemp"].mean()) if has_track_temp else None,
        "wind_direction": (float(df["WindDirection"].mean()) if has_wind_direction else None),
        "wind_speed": float(df["WindSpeed"].mean()) if has_wind_speed else None
    }

def sync_weather_from_fastf1():
    """
    Loads all races from the database and for each race loads all sessions.
    Tries to load the same event from FastF1.
    Skips testing events due to inconsistent FastF1 event mapping.
    For each session:
    - retrieves session-level weather data
    - calculates aggregate metrics (aggregate_session_weather)
    - saves aggregated weather data to the Weather table in the database
      (per race_id + session_id)
    Skips sessions that fail to load or return missing weather data.
    """
    db: Session = database.SessionLocal()

    try:
        # load all races from the database
        races = db.query(models.Race).all()

        for race in races:
            year = race.year
            race_name = race.race_name.strip()

            print(f"{year} | {race_name}")

            # skip if it's a testing event
            if "Testing" in race_name:
                print("Skipping testing event (FastF1 name mismatch).")
                continue

            # load all sessions for that race
            sessions = (db.query(models.Session).filter(models.Session.race_id == race.race_id).all())

            for s in sessions:
                openf1_session_name = s.session_name

                # map OpenF1 name to FastF1 name
                fastf1_session_name = SESSION_MAPPING.get(openf1_session_name)
                if not fastf1_session_name:
                    continue

                print(f"{openf1_session_name} - {fastf1_session_name}")

                # for error logging
                session_desc = f"{year} {race_name} - {openf1_session_name}/{fastf1_session_name}"

                # skip duplicates
                existing_weather = (
                    db.query(models.Weather.weather_id)
                    .filter(
                        models.Weather.race_id == race.race_id,
                        models.Weather.session_id == s.session_id
                    )
                    .first()
                )

                if existing_weather:
                    print("Weather already exists for this session.")
                    continue

                try:
                    # load FastF1 session by year, race name and session name
                    session = fastf1.get_session(year, race_name, fastf1_session_name)
                    session.load()

                    # retrieve weather data
                    weather_data = session.weather_data

                    if weather_data is None or weather_data.empty:
                        print("No weather data in FastF1 for this session.")
                        continue

                    # aggregate metrics into a dict
                    aggregate = aggregate_session_weather(weather_data)
                    if not aggregate:
                        continue

                    # create a Weather record in the database
                    weather = models.Weather(
                        race_id=race.race_id,
                        session_id=s.session_id,

                        air_temp=aggregate["air_temp"],
                        humidity=aggregate["humidity"],
                        pressure=aggregate["pressure"],
                        rainfall=aggregate["rainfall"],
                        track_temp=aggregate["track_temp"],
                        wind_direction=aggregate["wind_direction"],
                        wind_speed=aggregate["wind_speed"]
                    )

                    db.add(weather)

                    try:
                        db.commit()
                        print("Weather synced.")
                    except IntegrityError:
                        db.rollback()
                        print("Skipped duplicates.")

                except Exception as e:
                    print(f"Error loading {session_desc}: {e}")
                    db.rollback()
                    continue
    finally:
        db.close()

if __name__ == "__main__":
    sync_weather_from_fastf1()