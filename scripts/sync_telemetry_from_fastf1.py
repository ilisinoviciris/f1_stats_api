import fastf1
import pandas as pd
from pathlib import Path
from app import database, models
from sqlalchemy.orm import Session

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
    "Sprint Shootout": "Sprint Shootout", # for 2023 season
    "Sprint Qualifying": "Sprint Qualifying" # for 2024 and 2025 season
}

# aggregate telemetry for one lap
def aggregate_lap_telemetry(lap_telemetry: pd.DataFrame) -> dict:
    """
    Aggregates per-lap telemetry metrics from FastF1 Car Telemetry data:
    - avg_speed: average speed (km/h)
    - mean_rpm: average rpm
    - median_gear: median gear
    - throttle_usage: % time on throttle > 0.1 - eliminates values that aren't actual acceleration
    - brake_usage: % time on brake > 0.1 or True 
    - drs_usage: % time with open DRS == 1 
    """
    # if there's no data for that lap return empty
    if lap_telemetry is None or lap_telemetry.empty:
        return {}

    df = lap_telemetry

    total_samples = len(df)

    # if a lap has no telemetry samples, return empty metrics to avoid calculation errors
    if total_samples == 0:
        return {}

    # safe access za stupce
    has_speed = "Speed" in df.columns
    has_rpm = "RPM" in df.columns
    has_gear = "nGear" in df.columns
    has_throttle = "Throttle" in df.columns
    has_brake = "Brake" in df.columns
    has_drs = "DRS" in df.columns

    # calculating if brake is used for both boolean and numeric value
    if has_brake:
        if df["Brake"].dtype == bool:
            brake_active = df["Brake"]
        else:
            brake_active = df["Brake"] > 0.1
        brake_usage = float(brake_active.sum() / total_samples)
    else:
        brake_usage = None

    throttle_usage = (
        float((df["Throttle"] > 0.1).sum() / total_samples) if has_throttle else None
    )        

    drs_usage = (
        float((df["DRS"] == 1).sum() / total_samples) if has_drs else None
    )

    return {
        "avg_speed": float(df["Speed"].mean()) if has_speed else None,
        "mean_rpm": float(df["RPM"].mean()) if has_rpm else None,
        "median_gear": float(df["nGear"].median()) if has_gear else None,
        "throttle_usage": throttle_usage,
        "brake_usage": brake_usage,
        "drs_usage": drs_usage
    }

def sync_telemetry_from_fastf1():
    """
    Loads all races from the database and for each race loads all sessions.
    Tries to load the same event from FastF1. 
    Skips testing events due to inconsistent FastF1 event mapping.
    For each lap, for each driver:
    - retrieves lap-level telemetry data
    - calculates aggregate metrics (aggregate_lap_telemetry)
    - saves aggregated telemetry data to the Telemetry table in the database (per race_id + session_id + driver_number + lap_number)
    Skips sessions that fail to load or return missing lap or telemetry data.
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

                try:
                    # load FastF1 session by year, race name and session name
                    session = fastf1.get_session(year, race_name, fastf1_session_name)
                    session.load()
                    fastf1_laps = session.laps.copy()

                    # skip sessions where FastF1 does not return lap data
                    if fastf1_laps.empty:
                        print("No laps in FastF1 for this session.")
                        continue

                    for driver_acronym in fastf1_laps["Driver"].unique():
                        driver_acronym = str(driver_acronym).upper()

                        # all laps for that driver
                        driver_laps = fastf1_laps.pick_drivers(driver_acronym)

                        # iterate through laps in FastF1 for that driver
                        for _, lap in driver_laps.iterrows():
                            lap_number = int(lap["LapNumber"]) 

                            # find the correspoding lap in the database
                            db_lap = (
                                db.query(models.Lap)
                                .select_from(models.Lap)
                                .join(models.Driver, models.Lap.driver_number == models.Driver.driver_number)
                                .filter(
                                    models.Lap.session_id == s.session_id,
                                    models.Driver.name_acronym == driver_acronym,
                                    models.Lap.lap_number == lap_number                                
                                ).first())

                            if not db_lap:
                                continue
                            
                            # retrieve telemetry at lap level
                            try:
                                lap_telemetry = lap.get_car_data()
                            except Exception:
                                continue

                            if lap_telemetry is None or lap_telemetry.empty:
                                continue 

                            # aggregate metrics into a dict
                            aggregate = aggregate_lap_telemetry(lap_telemetry)
                            if not aggregate:
                                continue

                            # create a Telemetry record in the database
                            telemetry = models.Telemetry(
                                race_id=db_lap.race_id,
                                session_id=db_lap.session_id,
                                lap_number=db_lap.lap_number,
                                driver_number=db_lap.driver_number,

                                avg_speed=aggregate["avg_speed"],
                                mean_rpm=aggregate["mean_rpm"],
                                median_gear=aggregate["median_gear"],
                                throttle_usage=aggregate["throttle_usage"],
                                brake_usage=aggregate["brake_usage"],
                                drs_usage=aggregate["drs_usage"]
                            )

                            db.add(telemetry)

                    db.commit()
                    print("Telemetry synced.")
            
                except Exception as e:
                    print(f"Error loading {session}: {e}")
                    continue

    finally:
        db.close()

if __name__ == "__main__":
    sync_telemetry_from_fastf1()
