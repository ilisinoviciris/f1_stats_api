import pandas as pd
from app import database, models

def clean_laps_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove:
    - NULL values for lap_duration, tyre_compound, sectors
    - out laps
    - outliers (very long or very short laps)
    - if any of duration sectors is NULL
    """

    # remove laps where lap_duration is NULL
    df = df[df["lap_duration"].notnull()]

    # remove laps with NULL or UNKNOWN tyre_compound
    df = df[df["tyre_compound"].notnull()]
    df = df[df["tyre_compound"] != "UNKNOWN"]

    # remove outlaps
    if "is_pit_out_lap" in df.columns:
        df = df[df["is_pit_out_lap"] == False]

    # remove outliers
    df = df[(df["lap_duration"] > 60) & (df["lap_duration"] < 150)]

    # remove unless all sectors have assigned value
    df = df[df[["duration_sector_1", "duration_sector_2", "duration_sector_3"]].notnull().all(axis=1)]

    # reset index
    return df.reset_index(drop=True) 

def export_laps_to_csv(output_file: str = "laps_dataset.csv"):
    db = database.SessionLocal()

    # join laps + races + drivers + stints
    try:
        query = (
            db.query(
                models.Lap.race_id,
                models.Lap.session_id,
                models.Session.session_name,
                models.Driver.driver_id,
                models.Race.location.label("circuit_location"),
                models.Lap.lap_number,
                models.Stint.stint_number,
                (models.Lap.lap_number - models.Stint.lap_start + 1).label("stint_lap_number"),
                models.Stint.tyre_compound,
                models.Lap.duration_sector_1,
                models.Lap.duration_sector_2,
                models.Lap.duration_sector_3,
                models.Lap.lap_duration
            )
            .join(models.Race, models.Lap.race_id == models.Race.race_id)
            .join(models.Session, models.Lap.session_id == models.Session.session_id)
            .join(models.Driver, models.Lap.driver_number == models.Driver.driver_number)
            .join(
                models.Stint,
                (models.Lap.race_id == models.Stint.race_id) &
                (models.Lap.session_id == models.Stint.session_id) &
                (models.Lap.driver_number == models.Stint.driver_number) &
                (models.Lap.lap_number >= models.Stint.lap_start) &
                (models.Lap.lap_number <= models.Stint.lap_end)
            )
            # filter only Race and Practice 2
            .filter(models.Session.session_name.in_(["Race", "Practice 2"]))
        )

        df = pd.DataFrame(query.all(), columns=[
            "race_id",
            "session_id",
            "session_name",
            "driver_id",
            "circuit_location",
            "lap_number",
            "stint_number",
            "stint_lap_number",
            "tyre_compound",
            "duration_sector_1",
            "duration_sector_2",
            "duration_sector_3",
            "lap_duration"
        ])

        # clean dataframe
        df_clean = clean_laps_dataframe(df)

        # export to csv file
        df_clean.to_csv(output_file, index=False)
        print(f"Laps dataset exported to {output_file} containing ({len(df_clean)} rows).")

    finally:
        db.close()

if __name__ == "__main__":
    export_laps_to_csv()
    