import httpx
from sqlalchemy.orm import Session
from app import database, models, schemas
from app.repositories import stint_repository

OPENF1_STINTS_URL = "https://api.openf1.org/v1/stints"

# fetch all stints for all races from OpenF1 API and save/update them in the database
# returns count of created and updated stints
def sync_all_stints():
    db: Session = database.SessionLocal()
    try:
        races = db.query(models.Race).all()
        print(f"Found {len(races)} races in database.")

        total_created = 0
        total_updated = 0

        for race in races:
            race_id = race.race_id
            print(f"Fetching stints for race_id={race_id} ({race.race_name})")

            try:
                response = httpx.get(OPENF1_STINTS_URL, params={"meeting_key": race_id}, timeout=10)
                response.raise_for_status()
                stints_json = response.json()
            except httpx.HTTPError as e:
                print(f"Failed to retrieve stints for race_id={race_id}: {str(e)}")
                continue

            created = 0
            updated = 0

            for s in stints_json:
                stint_data = schemas.StintCreate(
                    race_id = race_id,
                    session_id = s.get("session_key"),
                    driver_number = s.get("driver_number"),
                    stint_number = s.get("stint_number"),
                    lap_start = s.get("lap_start"),
                    lap_end = s.get("lap_end"),
                    tyre_compound = s.get("compound"),
                    tyre_age_at_start = s.get("tyre_age_at_start")
                ) 

                stint_exists = db.query(models.Stint).filter(
                    models.Stint.race_id == stint_data.race_id,
                    models.Stint.session_id == stint_data.session_id,
                    models.Stint.driver_number == stint_data.driver_number,
                    models.Stint.stint_number == stint_data.stint_number
                ).first()
                
                if stint_exists:
                    update_data = stint_data.model_dump(exclude_unset=True)
                    for field, value in update_data.items():
                        if value is not None:
                            setattr(stint_exists, field, value)
                    db.commit()
                    db.refresh(stint_exists)
                    updated += 1
                else:
                    stint_repository.create_stint(db, stint_data)
                    created += 1

            print(f"race_id={race_id}: {created} created, {updated} updated, total={len(stints_json)}")

            total_created += created
            total_updated += updated

        print(f"\nAll races synced. Created={total_created}, Updated={total_updated}")

    finally:
        db.close()

if __name__ == "__main__":
    sync_all_stints()
