import fastf1
from pathlib import Path
from app import database, models
from sqlalchemy.orm import Session

# enable cache directory
cache_dir = Path("data/fastf1_cache")
cache_dir.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(str(cache_dir))

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

def sync_fastf1_data():
    """
    Fetches and syncs FastF1 data (pit_in_time, pit_out_time, track_status) to the already created table laps.
    """
    db: Session = database.SessionLocal()

    try:
        # load all races from the database
        races = db.query(models.Race).all()

        for race in races:
            year = race.year
            race_name = race.race_name.strip()

            print(f"{year} -> {race_name}")

            # load all sessions for that race
            sessions = db.query(models.Session).filter(models.Session.race_id == race.race_id).all()

            for s in sessions:
                session_name = s.session_name

                # map OpenF1 name to FastF1 name
                fastf1_session_name = SESSION_MAPPING.get(session_name)
                if not fastf1_session_name:
                    continue

                print(f"{session_name} or {fastf1_session_name}")

                try:
                    # load FastF1 session by year, race name and session name
                    session = fastf1.get_session(year, race_name, fastf1_session_name)
                    session.load()
                    fastf1_laps = session.laps.copy()

                    # add only relevant FastF1 columns
                    fastf1_laps["pit_in_time"] = (fastf1_laps["PitInTime"].dt.total_seconds() 
                                                  if "PitInTime" in fastf1_laps 
                                                  else None)
                    fastf1_laps["pit_out_time"] = (fastf1_laps["PitOutTime"].dt.total_seconds() 
                                                   if "PitOutTime" in fastf1_laps 
                                                   else None)
                    fastf1_laps["track_status"] = fastf1_laps.get("TrackStatus", None)
                    fastf1_laps["lap_number"] = fastf1_laps["LapNumber"]
                    fastf1_laps["driver"] = fastf1_laps["Driver"].str.upper()

                    updated_count = 0

                    # itterate through every FastF1 lap and try to find the same one in local database
                    for _, lap in fastf1_laps.iterrows():
                        driver_acronym = lap["driver"]
                        lap_number = int(lap["lap_number"])

                        # join by 'driver_number' because table Laps doesn't have driver_id
                        db_lap = (
                            db.query(models.Lap)
                            .select_from(models.Lap)
                            .join(models.Driver, models.Lap.driver_number == models.Driver.driver_number)
                            .filter(
                                models.Lap.session_id == s.session_id,
                                models.Driver.name_acronym == driver_acronym,
                                models.Lap.lap_number == lap_number,
                            ).first())

                        # if the lap exists update it with new columns
                        if db_lap:
                            db_lap.pit_in_time = lap["pit_in_time"]
                            db_lap.pit_out_time = lap["pit_out_time"]
                            db_lap.track_status = lap["track_status"]
                            updated_count += 1

                    db.commit()
                    print(f"For {session_name} — updated {updated_count} laps.")

                except Exception as e:
                    print(f"Error loading {session_name}: {e}")
                    continue

    finally:
        db.close()

if __name__ == "__main__":
    sync_fastf1_data()