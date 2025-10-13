"""
Adds new additional lap columns from FastF1 python library to the 'laps' table in the existing local SQLite database.
"""

from app import database
from sqlalchemy.orm import Session
from sqlalchemy import text

db: Session = database.SessionLocal()

db.execute(text("ALTER TABLE laps ADD COLUMN pit_in_time REAL;"))
db.execute(text("ALTER TABLE laps ADD COLUMN pit_out_time REAL;"))
db.execute(text("ALTER TABLE laps ADD COLUMN track_status TEXT;"))

db.commit()
db.close()