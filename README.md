# REST API Formula 1 Statistics Project

## A learning project that demonstrates how to build a REST API with FastAPI.

This project is built for learning purposes with a goal of practicing backend development, data engineering basics and containerization (Docker).

## Features of this project:
- `GET /` -> Root endpoint
- `GET /healthz` -> Health check endpoint
- `POST /drivers/` -> Add a new driver
- `GET /drivers/ ` -> Retrieve all drivers
- `GET /drivers/{driver_id}` -> Retrieve a driver by driver_id
- `PUT /drivers/{driver_id}` -> Update driver information
- `DELETE /drivers/{driver_id}` -> Delete a driver
- `POST /drivers/sync` -> Fetch drivers from OpenF1 API and store/update in local database

## Project highlights:
- Drivers are fetched directly directly from OpenF1 API and stored/updated locally.
- Database model (`app/models.py`) uses `driver_id` as the primary_key (generated from `full_name` e.g. `"Charles LECLERC"` to `"charles_leclerc"`).
- `country_code` is handled with a fallback rule: if missing in one record, it is searched across all entries for that driver.
- Centralized **exception handling** is added in `main.py` for database errors, external API errors and unexpected server errors.
- **Logging** is enabled across the project to capture errors and debug information.
- **Automated tests** are included (`tests/test_drivers.py`) to validate driver endpoints in addition to Postman testing.

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

## Database setup:
This project uses **SQLite** as the database (for now).
The database file `f1_stats.db` will be created automatically in project root when the app is started.
- SQLAlchemy is used as the ORM.
- Database connection is created in `app/database.py`.
- Models are defined in `app/models.py`.

## Testing API in Postman:
This API can be tested in two ways:
1. Using the [`Postman collection file`](./f1_stats_api.postman_collection.json).
2. Running automated tests with **pytest**:
    ```bash
    pytest -v
    ```

### Example requests:

#### 1. Create a new driver
`POST /drivers/`
```json
{
    "full_name": "Test TESTING",
    "first_name": "Test",
    "last_name": "Testing",
    "driver_number": 35,
    "name_acronym": "TES",
    "team_name": "Red Bull Racing",
    "country_code": "CRO",
    "driver_id": "test_testing"
}
```

#### 2. Update a driver (only selected fields)
`PUT /drivers/test_testing`
```json
{
    "driver_number": 50,
    "team_name": "Ferrari"
}
```

#### 3. Delete a driver
`DELETE /drivers/test_testing`
```json
{
    "detail": "Driver 'test_testing' is deleted."
}
```

#### 4. Sync drivers from OpenF1 API
`POST /drivers/sync`
```json
{
    "created": 84,
    "updated": 2389,
    "total": 2343
}
```