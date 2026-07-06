import pandas as pd

def calculate_driver_consistency(laps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate race-level driver consistency metrics from lap data.
    The function groups lap data by race and driver, then calculates:
    - average lap time
    - lap time standard deviation
    - coefficient of variation
    - consistency rank within each race
    Lower lap time variability means higher consistency.
    """
    df = laps_df.copy()

    # remove laps where lap_duration is NULL
    df = df[df["lap_duration"].notna()]

    # remove outlaps
    df = df[df["is_pit_out_lap"] != True]

    # group by race and driver and calculate lap-time statistics
    grouped = (df.groupby(["race_id", "driver_number"])
               .agg(
                   avg_lap_time=("lap_duration", "mean"),
                   lap_time_std=("lap_duration", "std"),
                   lap_count=("lap_duration", "count"),
                   )
                   .reset_index()
    )

    # normalize variability by average lap time
    grouped["consistency_score"] = grouped["lap_time_std"] / grouped["avg_lap_time"]

    # remove drivers with too few valid laps
    grouped = grouped[grouped["lap_count"] >= 5]

    # rank drivers within each race
    grouped["consistency_rank"] = (grouped.groupby("race_id")["consistency_score"]
        .rank(method="dense", ascending=True)
        .astype(int)
    )

    return grouped.sort_values(["race_id", "consistency_rank"])