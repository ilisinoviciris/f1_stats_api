import pandas as pd


def calculate_race_pace(laps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate representative race pace for each driver within each race.
    The function uses median lap time to reduce the impact of unusually slow
    laps and ranks drivers based on their typical race pace.
    """
    df = laps_df.copy()

    # remove laps where lap_duration is NULL
    df = df[df["lap_duration"].notna()]

    # remove outlaps 
    df = df[df["is_pit_out_lap"] != True]

    # calculate representative race pace for each driver and race
    grouped = (
        df.groupby(["race_id", "driver_number"])
        .agg(
            median_lap_time=("lap_duration", "median"),
            lap_count=("lap_duration", "count"),
        )
        .reset_index()
    )

    # keep only drivers with enough valid laps
    grouped = grouped[grouped["lap_count"] >= 5].copy()

    # find the fastest representative pace within each race
    grouped["best_race_pace"] = (grouped.groupby("race_id")["median_lap_time"].transform("min"))

    # calculate the gap to the best race pace in seconds per lap
    grouped["pace_delta"] = (grouped["median_lap_time"] - grouped["best_race_pace"])

    # rank drivers within each race (lower median lap time means better pace)
    grouped["pace_rank"] = (grouped.groupby("race_id")["median_lap_time"]
        .rank(method="dense", ascending=True)
        .astype(int)
    )

    return grouped.sort_values(["race_id", "pace_rank"])