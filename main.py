from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "F1 STATS API IS WORKING!"}

@app.get("/healthz")
def health():
    return {"status": "OK"}
