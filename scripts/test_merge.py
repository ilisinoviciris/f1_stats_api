"""
Test merge between OpenF1 and FastF1 data.
"""

from app import database, models
from sqlalchemy.orm import Session
import pandas as pd
import fastf1
from pathlib import Path
from sqlalchemy import create_engine

# initialize cache directory
cache_dir = Path("data/fastf1_cache")
cache_dir.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

# session mapping between OpenF1 and FastF1 for differently named practice sessions (FP1/2/3 vs. Practice 1/2/3)
SESSION_MAPPING = {
    "FP1": "Practice 1",
    "FP2": "Practice 2",
    "FP3": "Practice 3",
    "Qualifying": "Qualifying",
    "Race": "Race",
    "Sprint": "Sprint",
    "Sprint Shootout": "Sprint Shootout"
}

db: Session = database.SessionLocal()

def orm_to_df(data):
    df = pd.DataFrame([row.__dict__ for row in data])
    return df.drop(columns=["_sa_instance_state"], errors="ignore")

# load tables from ORM
laps_df = orm_to_df(db.query(models.Lap).all())
sessions_df = orm_to_df(db.query(models.Session).all())
races_df = orm_to_df(db.query(models.Race).all())
drivers_df = orm_to_df(db.query(models.Driver).all())

db.close()

# merge laps + sessions 
laps_sessions_merged = laps_df.merge(sessions_df, on="session_id", how="left")

# if there's duplicates, choose one columns for 'race_id'
if "race_id_x" in laps_sessions_merged.columns:
    laps_sessions_merged["race_id"] = laps_sessions_merged["race_id_x"]
    laps_sessions_merged = laps_sessions_merged.drop(columns=["race_id_x", "race_id_y"], errors="ignore")

# merge with races + drivers
openf1_merged = (
    laps_sessions_merged
    .merge(races_df, on="race_id", how="left")
    .merge(drivers_df, on="driver_number", how="left")
)

# convert 'race_name' to lowercase for easier comparison
# convert 'name_acronym' to uppercase
openf1_merged["race_name"] = openf1_merged["race_name"].str.lower().str.strip()
openf1_merged["session_name"] = openf1_merged["session_name"].str.strip()
openf1_merged["name_acronym"] = openf1_merged["name_acronym"].str.upper()

# test event 
year = 2023
race_name = "Bahrain Grand Prix"
session_name = "Practice 2"

# load session from FastF1
session = fastf1.get_session(year, race_name, session_name)
session.load() 
 # use a copy of session
fastf1_merged = session.laps.copy()

# assign different names for data from FastF1
fastf1_merged = fastf1_merged.assign(
    lap_time_s = fastf1_merged["LapTime"].dt.total_seconds(),
    event_name = session.event["EventName"].lower(),
    year = session.event.year,
    session_name = SESSION_MAPPING.get(session.name, session_name),
    driver = fastf1_merged["Driver"].str.upper(),
    lap_number = fastf1_merged["LapNumber"]
)

# merge local database (OpenF1 data) + FastF1 by:
#  - year -> (year/year)
#  - name of event (race_name/event_name)
#  - type of session (session_name/session_name)
#  - driver (name_acronym/driver)
#  - lap number (lap_number/lap_number)
all_merged = pd.merge(
    openf1_merged,
    fastf1_merged,
    left_on=["year", "race_name", "session_name", "name_acronym", "lap_number"],
    right_on=["year", "event_name", "session_name", "driver", "lap_number"],
    how="inner",
    suffixes=("_openf1", "_fastf1")
)

# print first 10 rows with times from both sources
print(all_merged[["year", "race_name", "session_name", "name_acronym", "lap_number", "lap_duration", "lap_time_s"]].head(10))

# calculate number of laps from both sources and number of merged laps
total_openf1_laps = len(openf1_merged)
total_fastf1_laps = len(fastf1_merged)
merged_laps = len(all_merged)

# calculate accuracy from both sources
match_rate_openf1 = (merged_laps / total_openf1_laps) * 100 if total_openf1_laps > 0 else 0
match_rate_fastf1 = (merged_laps / total_fastf1_laps) * 100 if total_fastf1_laps > 0 else 0

# print all calculations
print(f"OpenF1 (local database) laps total: {total_openf1_laps}")
print(f"FastF1 laps total: {total_fastf1_laps}")
print(f"Merged laps: {merged_laps}")
print(f"Match rate vs OpenF1 (local database): {match_rate_openf1:.2f}%")
print(f"Match rate vs FastF1: {match_rate_fastf1:.2f}%")
