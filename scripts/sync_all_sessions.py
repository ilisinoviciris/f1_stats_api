import httpx
from sqlalchemy.orm import Session
from app import database, models, schemas
from app.repositories import session_repository
import time

OPENF1_SESSIONS_URL = "https://api.openf1.org/v1/sessions"

# fetch sessions from OpenF1 API and save/update them in the database
# returns count of created and updated sessions
def sync_all_sessions():
    db: Session = database.SessionLocal()
    try:
        races = db.query(models.Race).all()
        print(f"Found {len(races)} races in database.")

        total_created = 0
        total_updated = 0

        for race in races:
            race_id = race.race_id
            print(f"Fetching sessions for race_id={race_id} ({race.race_name})")

            existing_sessions = db.query(models.Session).filter(models.Session.race_id == race_id).all()
            if existing_sessions:
                print(f"Skipping race_id={race_id} ({race.race_name}) - already created.")
                continue

            try:
                response = httpx.get(OPENF1_SESSIONS_URL, params={"meeting_key": race_id}, timeout=10)
                response.raise_for_status()
                sessions_json = response.json()
            except httpx.HTTPError as e:
                print(f"Failed to retrieve sessions for race_id={race_id}: {str(e)}")
                continue

            created = 0
            updated = 0

            for s in sessions_json:
                session_data = schemas.SessionCreate(
                    session_id = s.get("session_key"),
                    race_id = s.get("meeting_key"),
                    session_name = s.get("session_name"),
                    session_type = s.get("session_type")
                ) 

                session_exists = db.query(models.Session).filter(models.Session.session_id == session_data.session_id).first()
                
                if session_exists:
                    update_data = session_data.model_dump(exclude_unset=True)
                    for field, value in update_data.items():
                        if value is not None:
                            setattr(session_exists, field, value)
                    db.commit()
                    db.refresh(session_exists)
                    updated += 1
                else:
                    session_repository.create_session(db, session_data)
                    created += 1

            print(f"race_id={race_id}: {created} created, {updated} updated, total={len(sessions_json)}")

            time.sleep(1.5)

            total_created += created
            total_updated += updated

        print(f"\nAll races synced. Created={total_created}, Updated={total_updated}")

    finally:
        db.close()

if __name__ == "__main__":
    sync_all_sessions()
