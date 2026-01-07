# Weather Data Collector and API

This project consists of a weather data collector and a FastAPI application that exposes the collected data. The data collector fetches hourly weather reports from `wttr.in`, stores them in a MongoDB database, and implements retry mechanisms for robust data collection. The FastAPI application provides endpoints to retrieve these stored weather reports. The entire setup is containerized using Docker and orchestrated with Docker Compose.

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Build and Run with Docker Compose](#build-and-run-with-docker-compose)
  - [Accessing the Services](#accessing-the-services)
- [Project Structure](#project-structure)

## Features

- **Hourly Weather Data Collection:** Automatically fetches weather data from `wttr.in` every hour.
- **Robustness:** Implements retry logic for both external API calls (wttr.in) and MongoDB connection attempts.
- **Data Persistence:** Stores weather reports in a MongoDB database.
- **FastAPI for Data Exposure:** Provides a RESTful API to access the collected weather data.
- **Dockerized:** Entire application is containerized for easy deployment and management.

## Architecture

The project is composed of five main services orchestrated by Docker Compose:

1.  **`mongo`**: A MongoDB database instance used for storing weather reports.
2.  **`app`**: A Python application (`app.py`) that acts as a scheduler. It connects to MongoDB, fetches weather data hourly, and saves it to the database.
3.  **`api`**: A FastAPI application (`api.py`) that connects to MongoDB and exposes API endpoints to retrieve the stored weather reports.
4.  **`alerter`**: A Python application (`alerter.py`) that runs a daily check for high winds and sends a notification if the wind speed is above a certain threshold.
5.  **`mcp`**: A Python application (`mcp/main.py`) that provides a tool-based interface to the API.

```
+----------------+       +----------------+       +----------------+
|    wttr.in     | <---> |      app       | <---> |     mongo      |
| (External API) |       | (Data Collector)|       |  (Database)    |
+----------------+       +----------------+       +----------------+
                                   ^
                                   |
                                   v
                             +----------------+       +-------------------+
                             |      api       | ----> |        mcp        |
                             |  (FastAPI App) |       | (MCP Server)      |
                             +----------------+       +-------------------+
                                   ^
                                   |
                                   v
                          (HTTP Clients / Browser)
```

## API Endpoints

The FastAPI service exposes the following endpoints (available on port `8000`):

-   **`GET /`**
    -   **Description:** Returns a welcome message.
    -   **Response:** `{"message": "Weather Data API."}`

-   **`GET /weather/{date}`**
    -   **Description:** Retrieves a weather report for a specific date.
    -   **Response:** A `WeatherReport` object.
    -   **HTTP Status Codes:** `200 OK` (if found), `404 Not Found` (if no report exists for that date).

-   **`GET /weather/latest`**
    -   **Description:** Retrieves the single most recent weather report stored in the database.
    -   **Response:** A `WeatherReport` object.
    -   **HTTP Status Codes:** `200 OK` (if found), `404 Not Found` (if no reports exist).

-   **`GET /logs`**
    -   **Description:** Retrieves a list of the most recent data fetching attempt logs.
    -   **Response:** A JSON array of `AttemptLog` objects. (Limited to 100 latest logs for performance).

-   **`GET /docs`**
    -   **Description:** Access the interactive API documentation (Swagger UI).

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

-   [Docker](https://www.docker.com/get-started) (Docker Engine and Docker Compose)

### Build and Run with Docker Compose

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd weather # or wherever your project directory is
    ```

2.  **Build and start the services:**
    This command will build the Docker images for the `app` and `api` services, pull the `mongo` image, and start all three services in detached mode.

    ```bash
    docker-compose up --build -d
    ```

    _Note: The `app` service will start fetching data hourly and on initial startup. It might take a moment for the first data to appear in the database._

### Accessing the Services

-   **FastAPI Application:**
    -   The API will be available at `http://localhost:8000`.
    -   Access the interactive API documentation (Swagger UI) at `http://localhost:8000/docs`.

-   **MCP Server:**
    -   The MCP server will be available at `http://localhost:8001`.

-   **MongoDB (Optional):**
    -   The MongoDB instance is exposed on port `27017` on your host machine. You can connect to it using a MongoDB client (e.g., MongoDB Compass, `mongosh`) at `mongodb://localhost:27017/`.
    -   The database name is `weather_db` and the collection names are `hourly_reports` and `attempts`.

### Stopping the Services

To stop and remove the containers, networks, and volumes (including MongoDB data):

```bash
docker-compose down -v
```

To stop only the containers without removing volumes:

```bash
docker-compose down
```

## Project Structure

```
.
├── api               # FastAPI application exposing weather data
├── app               # Hourly weather data collector and scheduler
├── alerter           # High wind alerter application
├── mcp               # MCP server
├── docker-compose.yml # Defines and orchestrates Docker services (mongo, app, api, alerter, mcp)
├── Dockerfile        # Dockerfile for the 'app' service (weather collector)
├── Dockerfile.api    # Dockerfile for the 'api' service (FastAPI)
├── Dockerfile.alerter # Dockerfile for the 'alerter' service (wind alerter)
├── Dockerfile.mcp    # Dockerfile for the 'mcp' service (MCP Server)
└── requirements.txt  # Python dependencies for both app and api services
```
