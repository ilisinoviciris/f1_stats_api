from fastapi import FastAPI
from app.database import Base, engine
from app import models

app = FastAPI()

Base.metadata.create_all(bind=engine)


# root
@app.get("/")
def root():
    return {"message": "F1 STATS API IS WORKING!"}

# check health
@app.get("/healthz")
def health():
    return {"status": "OK"}
