import httpx
from sqlalchemy.orm import Session
from app import database, models, schemas
from app.repositories import race_repository

OPENF1_RACES_URL = "https://api.openf1.org/v1/meetings"

# fetch races from OpenF1 API and save/update them in the database
# returns count of created and updated races
def sync_all_races():
    db: Session = database.SessionLocal()
    try:
        try:
            response = httpx.get(OPENF1_RACES_URL, timeout=10)
            response.raise_for_status()
            races_json = response.json()
        except httpx.HTTPError as e:
            print(f"Error retrieving races from OpenF1 API: {str(e)}")
            return

        created = 0
        updated = 0

        for r in races_json:
            race_id = r.get("meeting_key")

            race_data = schemas.RaceCreate(
                race_id=race_id,
                race_name=r.get("meeting_name"),
                circuit_name=r.get("circuit_short_name"),
                location=r.get("location"),
                country_name=r.get("country_name"),
                year=r.get("year")
            )

            race_exists = (db.query(models.Race).filter(models.Race.race_id == race_id).first())

            if race_exists:
                update_data = race_data.model_dump(exclude_unset=True)
                for field, value in update_data.items():
                    if value is not None:
                        setattr(race_exists, field, value)
                db.commit()
                db.refresh(race_exists)
                updated += 1
            else:
                race_repository.create_race(db, race_data)
                created += 1

        print(f"Races synced. Created={created}, Updated={updated}, Total={len(races_json)}")

    finally:
        db.close()


if __name__ == "__main__":
    sync_all_races()