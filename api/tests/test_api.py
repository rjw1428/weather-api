import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
import os
import sys
from unittest.mock import MagicMock, patch
from datetime import date, timedelta, datetime

# Add the parent directory to the path so we can import the api module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import app, WeatherReport

@pytest.fixture
def mock_mongo_client():
    with patch('api.get_mongo_client') as mock_get_mongo_client:
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_get_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        yield mock_collection

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_read_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Weather Data API."}

@pytest.mark.asyncio
async def test_get_latest_report(client: AsyncClient, mock_mongo_client):
    today = date.today().strftime("%Y-%m-%d")
    mock_mongo_client.find_one.return_value = {
        "_id": "60d5ec49e7ef42e3f8a3e3a0", # Explicitly a string
        "date": today,                     # Explicitly a string
        "hourly": [],
        "timestamp_recorded_utc": datetime.utcnow().isoformat()
    }
    response = await client.get("/weather/latest")
    assert response.status_code == 200
    assert response.json()["date"] == today

@pytest.mark.asyncio
@pytest.mark.parametrize("date_str, expected_date_str", [
    ("today", date.today().strftime("%Y-%m-%d")),
    ("tomorrow", (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")),
    ("yesterday", (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")),
    ("2024-01-01", "2024-01-01"),
])
async def test_get_report_by_date_str(client: AsyncClient, mock_mongo_client, date_str, expected_date_str):
    mock_mongo_client.find_one.return_value = {
        "_id": "60d5ec49e7ef42e3f8a3e3a0", # Explicitly a string
        "date": expected_date_str,         # Explicitly a string
        "hourly": [],
        "timestamp_recorded_utc": datetime.utcnow().isoformat()
    }
    response = await client.get(f"/weather/{date_str}")
    assert response.status_code == 200
    assert response.json()["date"] == expected_date_str

@pytest.mark.asyncio
async def test_get_report_by_date_invalid_format(client: AsyncClient, mock_mongo_client):
    response = await client.get("/weather/invalid-date")
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid date format. Please use YYYY-MM-DD or keywords: today, tomorrow, yesterday."}

@pytest.mark.asyncio
async def test_get_report_by_date_not_found(client: AsyncClient, mock_mongo_client):
    mock_mongo_client.find_one.return_value = None
    response = await client.get("/weather/2024-01-02")
    assert response.status_code == 404
    assert response.json() == {"detail": "No weather report found for date: 2024-01-02"}
