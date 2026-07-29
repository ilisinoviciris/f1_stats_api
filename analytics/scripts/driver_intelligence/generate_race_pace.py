import pandas as pd
from pathlib import Path
from app import database, models
from sqlalchemy.orm import Session
from analytics.driver_intelligence.race_pace import calculate_race_pace

def generate_race_pace():
    """
    Generate race pace metrics from lap data stored in the local database.
    The script loads laps using SQLAlchemy, calculates driver race pace metrics, and exports the results to a .csv file.
    """
    db: Session = database.SessionLocal()

    try:
        # load lap records from the database
        laps = db.query(models.Lap).all()

        # convert SQLAlchemy objects into a structure suitable for pandas
        rows = []
        for lap in laps:
            rows.append({
                "race_id": lap.race_id,
                "session_id": lap.session_id,
                "driver_number": lap.driver_number,
                "lap_number": lap.lap_number,
                "lap_duration": lap.lap_duration,
                "is_pit_out_lap": lap.is_pit_out_lap,
            })

        laps_df = pd.DataFrame(rows)

        if laps_df.empty:
            print("No laps found.")
            return

        # calculate race pace metrics using the analytics module
        race_pace_df = calculate_race_pace(laps_df)

        race_pace_df = race_pace_df.round(
            {
                "median_lap_time": 3,
                "best_race_pace": 3,
                "pace_delta": 3,
            }
        )

        # export results to the outputs folder
        output_dir = Path("analytics/outputs")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / "driver_race_pace.csv"
        race_pace_df.to_csv(output_path, index=False)

        print(f"Driver race pace metrics exported to {output_path}")
        print(f"Rows exported: {len(race_pace_df)}")

    finally:
        db.close()

if __name__ == "__main__":
    generate_race_pace()