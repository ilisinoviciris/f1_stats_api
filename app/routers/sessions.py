from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, database
from app.repositories import session_repository
import httpx

# initializing router 
router = APIRouter(prefix="/sessions", tags=["Sessions"])

OPENF1_SESSIONS_URL = "https://api.openf1.org/v1/sessions"

# dependency for the database
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# endpoint for retrieving all sessions -> GET /sessions/
@router.get("/", response_model=List[schemas.Session])
def get_all_sessions(db: Session = Depends(get_db)):
    return session_repository.get_all_sessions(db)

# endpoint for retrieving a session by session_id -> GET /sessions/{id}
@router.get("/{id}", response_model=schemas.Session)
def get_session_by_id(id: int, db: Session = Depends(get_db)):
    return session_repository.get_session_by_id(db, id)

# endpoint for creating a new session -> POST /sessions/
@router.post("/", response_model=schemas.Session, status_code=201)
def create_session(session: schemas.SessionCreate, db: Session = Depends(get_db)):
    return session_repository.create_session(db, session)

# endpoint for updating a session -> PUT /sessions/{id}
@router.put("/{id}", response_model=schemas.Session)
def update_session(id: int, session: schemas.SessionUpdate, db: Session = Depends(get_db)):
    return session_repository.update_session(db, id, session)

# endpoint for deleting a session -> DELETE /sessions/{id}
@router.delete("/{id}")
def delete_session(id: int, db: Session = Depends(get_db)):
    return session_repository.delete_session(db, id)

# fetch all sessions by race_id from OpenF1 API and save/update them in the database -> POST /sessions/sync/{race_id}
# returns count of created and updated session
@router.post("/sync/{race_id}")
def fetch_sessions(race_id: int, db: Session = Depends(get_db)):
    try:
        response = httpx.get(OPENF1_SESSIONS_URL, params={"meeting_key": race_id}, timeout=10)
        response.raise_for_status()
        sessions_json = response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error retrieving sessions from OpenF1 API: {str(e)}"
        )
    
    if not isinstance(sessions_json, list) or len(sessions_json) == 0:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OpenF1 API returned an invalid or empty response."
        )

    created = 0
    updated = 0

    for s in sessions_json:
        session_id = s.get("session_key")
        race_id = s.get("meeting_key")
        session_name = s.get("session_name")
        session_type = s.get("session_type")

        session_data = schemas.SessionCreate(
            session_id = session_id,
            race_id = race_id,
            session_name = session_name,
            session_type = session_type 
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
        
    return {"created": created, "updated": updated, "total": len(sessions_json)}


