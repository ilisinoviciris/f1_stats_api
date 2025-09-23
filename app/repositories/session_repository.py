from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models, schemas

# return all sessions from the database
def get_all_sessions(db: Session):
    return db.query(models.Session).all()

# return a session by session_id if it exists
def get_session_by_id(db: Session, id: int):
    session = db.query(models.Session).filter(models.Session.id == id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id='{id}' is not found."
        )
    return session

# create a new session in the database (if session_id doesn't already exist)
def create_session(db: Session, session: schemas.SessionCreate):
    session_exists = db.query(models.Session).filter(models.Session.session_id == session.session_id).first()
    if session_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Session with this session_id='{session.session_id}' already exists."
            )
    
    db_session = models.Session(**session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

# update a session
def update_session(db: Session, id: int, session_update: schemas.SessionUpdate):
    session_exists = db.query(models.Session).filter(models.Session.id == id).first()
    if not session_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Session with this id='{id}' is not found."
        )

    update_data = session_update.model_dump()
    for field, value in update_data.items():
        if value is not None:
            setattr(session_exists, field, value)

    db.commit()
    db.refresh(session_exists)
    return session_exists
    
# delete a session
def delete_session(db: Session, id: int):
    session_exists = db.query(models.Session).filter(models.Session.id == id).first()
    if not session_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Session with this id='{id}' is not found."
        )
    db.delete(session_exists)
    db.commit()
    return {"detail": f"Session '{id}' is deleted."}

