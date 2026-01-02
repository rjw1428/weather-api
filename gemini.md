# Weather Data Collector and API

This project is a weather data collection and API service.

## Purpose

The primary purpose of this project is to:
*   **Collect Weather Data:** Periodically fetch weather data from an external API (`wttr.in`).
*   **Store Data:** Persist the collected weather data in a MongoDB database.
*   **Expose Data via API:** Provide a RESTful API to access the stored weather data.
*   **Ensure Reliability:** Implement retry mechanisms for both fetching data and connecting to the database.

## Key Components

### `app.py` - The Data Collector

This script is responsible for the following:
*   **Scheduling:** Runs a job every hour to fetch weather data.
*   **Data Fetching:** Makes HTTP requests to the `wttr.in` API to get weather information.
*   **Retry Logic:** Includes a retry mechanism to handle transient network errors and API unavailability.
*   **Data Storage:** Connects to a MongoDB database and stores the hourly weather forecasts. It also logs the fetching attempts into a separate collection.

### `api.py` - The FastAPI Application

This script provides a RESTful API to access the data stored in the database. It includes the following features:
*   **Endpoints for Data Retrieval:** Exposes endpoints to get weather reports by date and the latest report.
*   **Endpoint for Logs:** Provides an endpoint to view the logs of data fetching attempts.
*   **Data Validation:** Uses Pydantic models to validate and serialize the data returned by the API.

### `alerter.py` - The Wind Alerter

This script is responsible for the following:
*   **Scheduling:** Runs a job every day to check for high winds.
*   **Data Fetching:** Makes HTTP requests to the `api` service to get weather information.
*   **Wind Alerting:** Sends a notification via a Google Cloud Function if the wind speed is above a certain threshold.

### `models.py` - Pydantic Models

This file contains the Pydantic models used for data validation and serialization in the `api.py` application. These models define the structure of the weather data returned by the API.

### `docker-compose.yml` and Dockerfiles

The project is fully containerized using Docker. The `docker-compose.yml` file orchestrates the services, including the `app` data collector, the `api` service, the `alerter` service, and the `mongo` database. The `Dockerfile`, `Dockerfile.api`, and `Dockerfile.alerter` are used to build the images for the respective services.

## Data Flow

1.  The `app` service, running in a Docker container, sends a request to the `wttr.in` API.
2.  The `wttr.in` API returns a JSON response with weather data.
3.  The `app` service processes the response, extracts the hourly forecast for each day, and saves it to the `hourly_reports` collection in the MongoDB database. The attempt logs are saved in the `attempts` collection.
4.  The `api` service, running in a separate Docker container, provides endpoints that query the MongoDB database.
5.  A client can make HTTP requests to the `api` service to retrieve the stored weather data.
