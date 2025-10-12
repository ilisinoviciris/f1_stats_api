# REST API Formula 1 Statistics Project

## A learning project that demonstrates how to build a REST API with FastAPI.

This project is built for learning purposes with a goal of practicing backend development, data engineering basics and containerization (Docker).

## Features of this project:
- `GET /` -> Root endpoint
- `GET /healthz` -> Health check endpoint

### Drivers
- `POST /drivers/` -> Add a new driver
- `GET /drivers/ ` -> Retrieve all drivers
- `GET /drivers/{driver_id}` -> Retrieve a driver by driver_id
- `PUT /drivers/{driver_id}` -> Update driver information
- `DELETE /drivers/{driver_id}` -> Delete a driver
- `POST /drivers/sync` -> Fetch drivers from OpenF1 API and store/update in local database

### Races
- `POST /races/` -> Add a new race
- `GET /races/ ` -> Retrieve all races
- `GET /races/{race_id}` -> Retrieve a race by race_id
- `PUT /racess/{race_id}` -> Update race information
- `DELETE /races/{race_id}` -> Delete a race
- `POST /races/sync` -> Fetch races from OpenF1 API and store/update in local database

### Sessions
- `POST /sessions/` -> Add a new session
- `GET /sessions/ ` -> Retrieve all sessions
- `GET /sessions/{id}` -> Retrieve a session by id
- `PUT /sessions/{id}` -> Update session information
- `DELETE /sessions/{id}` -> Delete a session
- `POST /sessions/{race_id}` -> Fetch all sessions by race_id from OpenF1 API and store/update in local database

### Stints
- `POST /stints/` -> Add a new stint
- `GET /stints/ ` -> Retrieve all stints
- `GET /stints/{stint_id}` -> Retrieve a stint by stint_id
- `PUT /stints/{stint_id}` -> Update stint information
- `DELETE /stints/{stint_id}` -> Delete a stint
- `POST /stints/{race_id}` -> Fetch all stints by race_id from OpenF1 API and store/update in local database

### Laps
- `POST /laps/` -> Add a new lap
- `GET /laps/ ` -> Retrieve all laps
- `GET /laps/{lap_id}` -> Retrieve a session by session_id
- `PUT /laps/{lap_id}` -> Update lap information
- `DELETE /laps/{lap_id}` -> Delete a lap
- `POST /laps/{race_id}` -> Fetch all laps by race_id from OpenF1 API and store/update in local database

## Project highlights:
- Drivers are fetched directly directly from OpenF1 API and stored/updated locally.
- Database model (`app/models.py`) uses `driver_id` as the primary_key (generated from `full_name` e.g. `"Charles LECLERC"` to `"charles_leclerc"`).
- `country_code` is handled with a fallback rule: if missing in one record, it is searched across all entries for that driver.
- Centralized **exception handling** is added in `main.py` for database errors, external API errors and unexpected server errors.
- **Logging** is enabled across the project to capture errors and debug information.
- **Automated tests** are included (`tests/test_drivers.py`, `tests/test_races.py`, `tests/test_sessions.py`, `tests/test_laps.py`) to validate driver, race, session and lap endpoints in addition to Postman testing.
- **Scripts** that fetch and store all sessions and laps into the database are included (`scripts/sync_all_sessions.py`, `scripts/sync_all_laps.py`, `scripts/sync_all_stints`).

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

## Project setup:
This project uses **SQLite** as the database (for now).
The database file `f1_stats.db` will be created automatically in project root when the app is started.
- SQLAlchemy is used as the ORM.
- Database connection is created in `app/database.py`.
- `app/models` -> contains SQLAlchemy database models, each representing a database table.
- `app/schemas` -> contains Pydantic schemas used for request validation and response formatting.
- `app/repositories` -> contains repository functions that handle database operations.
- `app/routers` -> contains API endpoints (routes) defined with FastAPI, connected to repositories and schemas.

## Testing API:
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
    "updated": 6304,
    "total": 6388
}
```

#### 5. Get all races
`GET /races/`
```json
{
    "race_id": 1140,
    "race_name": "Pre-Season Testing",
    "circuit_name": "Sakhir",
    "location": "Sakhir",
    "country_name": "Bahrain",
    "year": 2023
}
```

#### 6. Sync races from OpenF1 API
`POST /races/sync`
```json
{
    "created": 65,
    "updated": 0,
    "total": 65
}
```

## Sync scripts:
This project uses helper **scripts** that fetch and store large amount of data from sessions, stints and laps directly into the database. They are located in folder `scripts/`.

### Available scripts:
- `scripts/sync_all_sessions.py` -> fetches all sessions for all races stored in the database.
- `scripts/sync_all_stints.py` -> fetches all stints for all races stored in the database.
- `scripts/sync_all_laps.py` -> fetches all laps for all races stored in the database.

#### How to run:
From project root:
```bash
python -m scripts.sync_all_sessions
python -m scripts.sync_all_stints
python -m scripts.sync_all_laps
```

#### Example output:
```bash
Found 66 races in database.
Fetching sessions for race_id=1250 (Las Vegas Grand Prix)
race_id=1250: 5 created, 0 updated, total=5
```

### Export dataset
After syncing data, you can export the cleaned dataset into a .csv file for Machine Learning training:
```bash
python -m scripts.export_laps
```

## Machine Learning
This project includes a **Machine Learning** module for analyzing and predicting race pace evolution from created dataset (`laps_dataset.csv`).

### First model: Linear Regression model
- Training of a **Linear Regression** baseline model to predict lap time (lap_duration).
- Evaluation with metrics: R2, MAE, MSE, RMSE.
- Saving artifacts:
    - trained models
    - evaluation metrics
    - visualizations

## Test merge: local database (containing data from ONLY OpenF1) + FastF1 
This script compares lap data from **OpenF1 API** stored in project's local database with lap data from python library FastF1.
It merges laps + sessions + races + drivers and compares lap duration from both data sources.