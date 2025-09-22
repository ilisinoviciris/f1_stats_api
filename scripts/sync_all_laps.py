import httpx
from sqlalchemy.orm import Session
from app import database, models, schemas
from app.repositories import lap_repository

OPENF1_LAPS_URL = "https://api.openf1.org/v1/laps"

# fetch laps from OpenF1 API and save/update them in the database
# returns count of created and updated laps
def sync_all_laps():
    db: Session = database.SessionLocal()
    try:
        races = db.query(models.Race).all()
        print(f"Found {len(races)} races in database.")

        total_created = 0
        total_updated = 0

        for race in races:
            race_id = race.race_id
            print(f"Fetching laps for race_id={race_id} ({race.race_name})")

            try:
                response = httpx.get(OPENF1_LAPS_URL, params={"meeting_key": race_id}, timeout=10)
                response.raise_for_status()
                laps_json = response.json()
            except httpx.HTTPError as e:
                print(f"Failed to retrieve laps for race_id={race_id}: {str(e)}")
                continue

            created = 0
            updated = 0

            for l in laps_json:
                if l.get("lap_duration") is None:
                    continue

                lap_data = schemas.LapCreate(
                    race_id = race_id,
                    driver_number = l.get("driver_number"),
                    lap_number = l.get("lap_number"),
                    lap_duration = l.get("lap_duration", 0),
                    duration_sector_1 = l.get("duration_sector_1", 0),
                    duration_sector_2 = l.get("duration_sector_2", 0),
                    duration_sector_3 = l.get("duration_sector_3", 0),
                    i1_speed = l.get("i1_speed", 0),
                    i2_speed = l.get("i2_speed", 0),
                    st_speed = l.get("st_speed", 0),
                    is_pit_out_lap = l.get("is_pit_out_lap", False),
                    session_id = l.get("session_key"),
                    session_name = l.get("session_name") or "",
                    session_type = l.get("session_type") or ""
                ) 

                lap_exists = db.query(models.Lap).filter(
                    models.Lap.race_id == race_id,
                    models.Lap.session_id == lap_data.session_id,
                    models.Lap.driver_number == lap_data.driver_number,
                    models.Lap.lap_number == lap_data.lap_number
                    ).first()
                
                if lap_exists:
                    update_data = lap_data.model_dump(exclude_unset=True)
                    for field, value in update_data.items():
                        if value is not None:
                            setattr(lap_exists, field, value)
                    db.commit()
                    db.refresh(lap_exists)
                    updated += 1
                else:
                    lap_repository.create_lap(db, lap_data)
                    created += 1

            print(f"race_id={race_id}: {created} created, {updated} updated, total={len(laps_json)}")

            total_created += created
            total_updated += updated

        print(f"\nAll races synced. Created={total_created}, Updated={total_updated}")

    finally:
        db.close()

if __name__ == "__main__":
    sync_all_laps()
