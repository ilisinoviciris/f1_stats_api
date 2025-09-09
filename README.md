# REST API Formula 1 Statistics Project

## A learning project that demonstrates how to build a REST API with FastAPI.

This project is built for learning purposes with a goal of practicing backend development, data engineering basics, and containerization (Docker).

## Features of this project:
- `GET /` -> Root endpoint
- `GET /healthz` -> Health check endpoint

## How to install this project:
1. Create and activate virtual environment:
    ```bash 
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
2. Run the API:
    ```bash
    uvicorn app.main:app --reload
    ```
The API will be available at: http://localhost:8000/

## Testing API in Postman:
This API can be tested in Postman using the provided:
[`Postman collection file`](./f1_stats_api.postman_collection.json)
