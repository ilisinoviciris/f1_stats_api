from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite connection URL
DATABASE_URL = "sqlite:///./f1_stats.db"

# connection to the database
engine = create_engine (DATABASE_URL, connect_args={"check_same_thread": False})

# session factory for database operations (CRUD)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class for all ORM models
Base = declarative_base()