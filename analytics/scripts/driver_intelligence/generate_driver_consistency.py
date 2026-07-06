import pandas as pd
from pathlib import Path
from app import database, models
from sqlalchemy.orm import Session
from analytics.driver_intelligence.consistency import calculate_driver_consistency

def generate_driver_consistency():
    """
    Generate driver consistency metrics from the local database.
    The script loads lap data from the database, calculates race-level consistency metrics, and exports the results to a .csv file.
    """
    db: Session = database.SessionLocal()

    try:
        # load all lap records from the database
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

        # calculate consistency metrics using the analytics module
        consistency_df = calculate_driver_consistency(laps_df)

        consistency_df = consistency_df.round({
            "avg_lap_time": 3,
            "lap_time_std": 3,
            "consistency_score": 5,
        })

        # export results to the outputs folder
        output_dir = Path("analytics/outputs")
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / "driver_consistency.csv"
        consistency_df.to_csv(output_path, index=False)

        print(f"Driver consistency metrics exported to {output_path}")
        print(f"Rows exported: {len(consistency_df)}")

    finally:
        db.close()

if __name__ == "__main__":
    generate_driver_consistency()