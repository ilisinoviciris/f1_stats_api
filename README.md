# REST API Formula 1 Statistics Project

## Overview:
A learning project that demonstrates how to build a REST API with **FastAPI**, integrate two external data sources (OpenF1 + FastF1), store them in a local database and use the data for **machine learning analysis**.

## Features:

### API endpoints
- `GET /` -> Root endpoint
- `GET /healthz` -> Health check endpoint

#### Drivers
- `POST /drivers/` -> Add a new driver
- `GET /drivers/ ` -> Retrieve all drivers
- `GET /drivers/{driver_id}` -> Retrieve a driver by driver_id
- `PUT /drivers/{driver_id}` -> Update driver information
- `DELETE /drivers/{driver_id}` -> Delete a driver
- `POST /drivers/sync` -> Fetch drivers from OpenF1 API and store/update in local database

#### Races
- `POST /races/` -> Add a new race
- `GET /races/ ` -> Retrieve all races
- `GET /races/{race_id}` -> Retrieve a race by race_id
- `PUT /racess/{race_id}` -> Update race information
- `DELETE /races/{race_id}` -> Delete a race
- `POST /races/sync` -> Fetch races from OpenF1 API and store/update in local database

#### Sessions
- `POST /sessions/` -> Add a new session
- `GET /sessions/ ` -> Retrieve all sessions
- `GET /sessions/{id}` -> Retrieve a session by id
- `PUT /sessions/{id}` -> Update session information
- `DELETE /sessions/{id}` -> Delete a session
- `POST /sessions/{race_id}` -> Fetch all sessions by race_id from OpenF1 API and store/update in local database

#### Stints
- `POST /stints/` -> Add a new stint
- `GET /stints/ ` -> Retrieve all stints
- `GET /stints/{stint_id}` -> Retrieve a stint by stint_id
- `PUT /stints/{stint_id}` -> Update stint information
- `DELETE /stints/{stint_id}` -> Delete a stint
- `POST /stints/{race_id}` -> Fetch all stints by race_id from OpenF1 API and store/update in local database

#### Laps
- `POST /laps/` -> Add a new lap
- `GET /laps/ ` -> Retrieve all laps
- `GET /laps/{lap_id}` -> Retrieve a session by session_id
- `PUT /laps/{lap_id}` -> Update lap information
- `DELETE /laps/{lap_id}` -> Delete a lap
- `POST /laps/{race_id}` -> Fetch all laps by race_id from OpenF1 API and store/update in local database

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

## Data integation:

Data from **OpenF1** API (table drivers, races, sessions, stints and laps) and **FastF1** python library (additional lap data, telemetry is planned to be added) are merged and synchronized locally to produce a dataset for model training.

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
3. Sync via POSTMAN or HTTP requests like it's explained above in **Features**.
3. Automated sync via scripts in this order:
    ```bash
    python -m scripts.sync_all_sessions
    python -m scripts.sync_all_stints
    python -m scripts.sync_all_laps
    python -m scripts.test_merge
    python -m scripts.add_fastf1_laps_columns
    python -m scripts.add_sync_laps_from_fastf1
    ```
4. Export dataset for ML:
    ```bash 
    python -m scripts.export_laps
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

### Sync scripts:
This project uses helper **scripts** that fetch and store large amount of data from sessions, stints and laps directly into the database. They are located in folder `scripts/`.

#### Available scripts:
- `scripts/sync_all_sessions.py` -> fetches all sessions for all races stored in the database.
- `scripts/sync_all_stints.py` -> fetches all stints for all races stored in the database.
- `scripts/sync_all_laps.py` -> fetches all laps for all races stored in the database.
- `scripts/test_merge.py` -> test merge for OpenF1 and FastF1 data.
- `scripts/add_fastf1_laps_columns.py` -> adds new columns that will be synced from FastF1 to the existing table laps.
- `scripts/sync_laps_from_fastf1.py` -> fetched and syncs new lap data from FastF1
- `scripts/export_laps.py` -> exports dataset for ML.

## Machine Learning
This project includes a **Machine Learning** module for analyzing and predicting race pace evolution from created dataset (`laps_dataset.csv`). The models are not finished and will be worked on more after adding more features.

Saving artifacts for all models:
    - trained models (.pkl)
    - evaluation metrics (.json)
    - visualizations (.png)

### First model: Linear Regression model
- Target: lap_duration
- Input features: lap_number, stint_number, stint_lap_number, tyre_age_at_start, pit_in_time, pit_out_time, driver_id, tyre_compound, circuit_location, session_name
- Evaluation with metrics: 
    - R2: 0.6024,
    - MAE: 4.6014,
    - MSE: 72.0994,
    - RMSE: 8.4911.

### Second model: Random Forest model
- Target and input features same as in Linear Regression model.
- Contains Feature importance plot.
- Evaluation with metrics: 
    - R2: 0.9247,
    - MAE: 1.2130,
    - MSE: 13.6570,
    - RMSE: 3.6955.
    - Train R2: 0.9839
    - Test R2: 0.9247

### Third model: Tuned Random Forest model
After the baseline Random Forest Regressor was trained, a tuned version was developed using hyperparameter optimization.
Best hyperparameters:
    - n_estimators": 300,
    - min_samples_split": 2,
    - min_samples_leaf": 1,
    - max_features": "sqrt",
    - max_depth": 30.

## Next steps:
- add telemetry and weather data
- add feature engineering for race conditions
- upgrade ML models 
- migrate to PostgreSQL
- add containerization (Docker)
- add more visualizations for race analytics.

