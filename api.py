from fastapi import FastAPI, HTTPException, Request
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import os
import time
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from models import Hourly

app = FastAPI()
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="192.168.65.1")

@app.middleware("http")
async def log_ip_address(request: Request, call_next):
    """
    Middleware to log the client's IP address for each request.
    """
    timestamp = datetime.now()
    client_ip = request.client.host
    print(request.headers.get('X-Forwarded-For'))
    print(f"{timestamp} = API: Request from Client IP: {client_ip}")
    
    # Continue processing the request
    response = await call_next(request)
    
    return response

# --- Configuration ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
DB_NAME = "weather_db"
HOURLY_REPORTS_COLLECTION_NAME = "hourly_reports"
ATTEMPTS_COLLECTION_NAME = "attempts"

# MongoDB client instance
mongo_client_instance: Optional[MongoClient] = None

def get_mongo_client() -> MongoClient:
    """
    Establishes a connection to MongoDB with retry logic.
    """
    global mongo_client_instance
    if mongo_client_instance:
        return mongo_client_instance

    retries = 5
    while retries > 0:
        try:
            client = MongoClient(MONGO_URI)
            client.admin.command('ismaster')
            print("API: Successfully connected to MongoDB.")
            mongo_client_instance = client
            return client
        except ConnectionFailure as e:
            retries -= 1
            print(f"API: Could not connect to MongoDB: {e}. Retrying in 5 seconds...")
            time.sleep(5)
    raise ConnectionFailure("API: Failed to connect to MongoDB after several retries.")

@app.on_event("startup")
async def startup_db_client():
    """
    Connects to MongoDB on FastAPI startup.
    """
    try:
        get_mongo_client()
    except ConnectionFailure as e:
        print(f"API: Startup failed due to MongoDB connection issue: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_db_client():
    """
    Closes the MongoDB connection on FastAPI shutdown.
    """
    global mongo_client_instance
    if mongo_client_instance:
        mongo_client_instance.close()
        print("API: MongoDB connection closed.")

# Pydantic models for response data validation and serialization

class AttemptLog(BaseModel):
    id: str = Field(alias="_id")
    attempt_number: int
    timestamp_utc: datetime
    success: bool
    status_code: Optional[int]
    error: Optional[str]

    class Config:
        validate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid)
        }

    @validator("id", pre=True)
    def id_to_string(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

class WeatherReport(BaseModel):
    id: str = Field(alias="_id")
    date: str
    hourly: List[Hourly]
    timestamp_recorded_utc: datetime

    class Config:
        validate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid)
        }

    @validator("id", pre=True)
    def id_to_string(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

@app.get("/")
async def read_root():
    return {"message": "Weather Data API."}

@app.get("/weather/{date}", response_model=WeatherReport)
async def get_report_by_date(date: str):
    """
    Retrieve a weather report for a specific date.
    """
    try:
        client = get_mongo_client()
        db = client[DB_NAME]
        collection = db[HOURLY_REPORTS_COLLECTION_NAME]

        report = collection.find_one({"date": date})
        if report:
            return report
        raise HTTPException(status_code=404, detail=f"No weather report found for date: {date}")
    except ConnectionFailure as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/weather/latest", response_model=WeatherReport)
async def get_latest_report():
    """
    Retrieve the most recent weather report.
    """
    try:
        client = get_mongo_client()
        db = client[DB_NAME]
        collection = db[HOURLY_REPORTS_COLLECTION_NAME]

        latest_report = collection.find_one(sort=[("date", -1)])
        if latest_report:
            return latest_report
        raise HTTPException(status_code=404, detail="No weather reports found.")
    except ConnectionFailure as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/logs", response_model=List[AttemptLog])
async def get_all_logs():
    """
    Retrieve all attempt logs.
    """
    try:
        client = get_mongo_client()
        db = client[DB_NAME]
        collection = db[ATTEMPTS_COLLECTION_NAME]
        
        logs = list(collection.find().sort("timestamp_utc", -1).limit(100))
        return logs
    except ConnectionFailure as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
