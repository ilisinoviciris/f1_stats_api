# Formula 1 Analytics Platform

## Overview:
An ongoing Formula 1 analytics and data engineering project focused on backend development, ETL pipelines, telemetry processing and machine learning experimentation.

The project demonstrates how to build a REST API with **FastAPI**, integrate external data sources (OpenF1 + FastF1), design relational database schemas and process telemetry and weather data for analytics and **ML** use cases.

## Tech stack:

### Backend & API
- Python
- FastAPI
- SQLAlchemy
- Pydantic

### Data & Analytics
- Pandas
- NumPy
- scikit-learn

### Data Sources
- OpenF1 API
- FastF1

### Database 
- SQLite

### Testing & Tools 
- pytest
- Postman

## Features:

### Available API modules
- Drivers
- Races
- Sessions
- Stints
- Laps
- Telemetry
- Weather

The API supports CRUD operations, synchronization endpoints and analytics-related data retrieval.

#### Example endpoints
- `GET /drivers/` -> Retrieve all drivers
- `PUT /sessions/{id}` -> Update session information
- `POST /races/sync` -> Fetch races from OpenF1 API and synchronize them with the local database
- `DELETE /laps/{lap_id}` -> Delete a lap

## Testing API:
This API can be tested in two ways:
1. Using the [`Postman collection file`](./f1_stats_api.postman_collection.json).
2. Running automated tests with **pytest**:
    ```bash
    pytest -v
    ```

### Example requests:

#### Create a new driver
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

#### Retrieve race data
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

#### Synchronize races from OpenF1 API
`POST /races/sync`
```json
{
    "created": 33,
    "updated": 67,
    "total": 100
}
```

## Data integration:
The project uses custom synchronization scripts for sessions, stints, laps, telemetry and weather data ingestion. These ETL-style scripts automate data fetching, processing and storage into the local database.

Data from **OpenF1** API (`drivers`, `races`, `sessions`, `stints` and `laps`) and **FastF1** python library (additional lap data, telemetry and weather) are merged and synchronized locally to create datasets for analytics and machine learning use cases.

Telemetry data is retrieved from FastF1 at lap level, aggregated into structured telemetry features and stored in the `telemetry` table.

Weather data is retrieved from FastF1 session weather data, aggregated into structured session-level weather features and stored in the `weather` table.

## Getting started:
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
3. Sync via Postman or HTTP requests as explained above in **Features**.
4. Automated sync via scripts in this order:
    ```bash
    python -m scripts.sync_all_sessions
    python -m scripts.sync_all_stints
    python -m scripts.sync_all_laps
    python -m scripts.test_merge
    python -m scripts.add_fastf1_laps_columns
    python -m scripts.sync_laps_from_fastf1
    python -m scripts.sync_telemetry_from_fastf1
    python -m scripts.sync_weather_from_fastf1
    ```
5. Export dataset for ML:
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
This project uses helper **scripts** that fetch and store large amounts of data from sessions, stints, laps, telemetry and weather directly into the database. They are located in folder `scripts/`.

#### Available scripts:
- `scripts/sync_all_sessions.py` -> fetches all sessions for all races and stores them in the database (table sessions).
- `scripts/sync_all_stints.py` -> fetches all stints for all races and stores them in the database (table stints).
- `scripts/sync_all_laps.py` -> fetches all laps for all races and stores them in the database (table laps).
- `scripts/test_merge.py` -> test merge for OpenF1 and FastF1 data.
- `scripts/add_fastf1_laps_columns.py` -> adds new columns that will be fetched from FastF1 and stored to the existing table laps.
- `scripts/sync_laps_from_fastf1.py` -> fetches new lap data from FastF1 and stores them in the database to the existing table laps.
- `scripts/sync_telemetry_from_fastf1.py` -> fetches lap-level telemetry data from FastF1, aggregates telemetry metrics and stores them in the database (table telemetry).
- `scripts/sync_weather_from_fastf1.py` -> fetches session-level weather data from FastF1, aggregates weather metrics and stores them in the database (table weather).
- `scripts/export_laps.py` -> exports dataset for ML.

### Telemetry processing
Telemetry data is retrieved from FastF1 car telemetry and aggregated per lap to reduce the size of the dataset while preserving important driving metrics.
For each race and session stored in the database, the script loads the corresponding FastF1 session (with caching enabled).
Testing events are skipped due to inconsistent FastF1 event mapping.
For each driver and lap, car telemetry is fetched using lap.get_car_data().
Telemetry is aggregated into lap-level features and stored in the telemetry table using the unique key:
(race_id, session_id, driver_number, lap_number).

Aggregated telemetry features include:
- avg_speed -> average car speed during the lap (km/h)
- mean_rpm -> average engine RPM during the lap
- median_gear -> median gear used during the lap
- throttle_usage -> percentage of telemetry samples with throttle > 0.1
- brake_usage -> percentage of telemetry samples with braking (supports boolean and numeric brake signals)
- drs_usage -> percentage of lap time with DRS enabled

This aggregation allows telemetry data to be integrated with lap-level race data and used later for machine learning analysis.

### Weather processing
Weather data is retrieved from FastF1 session weather data and aggregated at session level. 
For each race and session stored in the database, the script loads the corresponding FastF1 session and extracts weather metrics from session.weather_data.

Aggregated weather features include:
- air_temp -> average air temperature during the session (°C)
- humidity -> average relative humidity (%)
- pressure -> average air pressure (mbar)
- rainfall -> indicates whether rainfall occurred during the session
- track_temp -> average track temperature during the session (°C)
- wind_direction -> average wind direction (°)
- wind_speed -> average wind speed (m/s)

The aggregated weather data is stored in the weather table and can later be integrated with lap-level race data for feature engineering and machine learning analysis.

## Machine Learning
This project currently includes initial machine learning experimentation for lap time prediction using the created dataset (`laps_dataset.csv`). 

The current ML workflow includes:
- dataset preparation
- feature engineering
- model training
- model evaluation
- saving model artifacts, metrics and visualizations

The target variable is `lap_duration`.

Current models:
- Linear Regression
- Random Forest Regressor
- Tuned Random Forest Regressor

The models currently use lap, stint, tyre, pit stop, driver, circuit and session-related features. Future iterations will include additional telemetry and weather-based features.

## Next steps:
- add advanced feature engineering for race conditions, telemetry and weather data
- improve telemetry and weather integration for more detailed race analysis
- expand machine learning experimentation and model evaluation
- migrate from SQLite to PostgreSQL
- add automated scheduled synchronization
- add containerization with Docker
- develop analytics visualizations and dashboards
- improve API endpoints for analytics and data exploration
- experiment with predictive and comparison-based race analytics

