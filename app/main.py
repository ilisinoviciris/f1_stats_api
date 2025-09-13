from fastapi import FastAPI
from app.database import Base, engine
from app import models
from app.routers import drivers

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


# root
@app.get("/")
def root():
    return {"message": "F1 STATS API IS WORKING!"}

# check health
@app.get("/healthz")
def health():
    return {"status": "OK"}

# add drivers router
app.include_router(drivers.router)
