from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from app.database import Base, engine
from app import models
from app.routers import drivers
import httpx
from sqlalchemy.exc import SQLAlchemyError
import logging

logging.basicConfig(
    level = logging.DEBUG,
    format = "%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# add drivers router
app.include_router(drivers.router)

# root
@app.get("/")
def root():
    return {"message": "F1 STATS API IS WORKING!"}

# check health
@app.get("/healthz")
def health():
    return {"status": "OK"}

# central exception handler for SQLAlchemy errors
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc: SQLAlchemyError):
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occured."}
    )

# central exception handler for httpx errors
@app.exception_handler(httpx.HTTPError)
async def httpx_exception_handler(request, exc: httpx.HTTPError):
    logger.error(f"External API error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "External API is unavailable."}
    )

# central exception handler for general uncaught exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.exception("Unexpected server error")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Unexpected server error occured."}
    )