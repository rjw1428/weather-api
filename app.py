import os
import time
import requests
import schedule
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# --- Configuration ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
WEATHER_URL = "http://wttr.in/18966?format=j1"
RETRY_DELAY_SECONDS = 10
MAX_RETRIES = 5
REQUEST_TIMEOUT_SECONDS = 10 # Timeout for the weather API request

def get_mongo_client():
    """
    Establishes a connection to MongoDB with retry logic.
    """
    retries = 5
    while retries > 0:
        try:
            client = MongoClient(MONGO_URI)
            # The ismaster command is cheap and does not require auth.
            client.admin.command('ismaster')
            logging.info("Successfully connected to MongoDB.")
            return client
        except ConnectionFailure as e:
            retries -= 1
            logging.error(f"Could not connect to MongoDB: {e}. Retrying in 5 seconds...")
            time.sleep(5)
    logging.error("Failed to connect to MongoDB after several retries. Exiting.")
    return None

def fetch_weather_data():
    """
    Fetches weather data from the wttr.in API with retry logic for timeouts.
    Records each attempt's success status.
    """
    attempts_log = []
    for attempt_num in range(MAX_RETRIES):
        attempt_info = {
            "attempt_number": attempt_num + 1,
            "timestamp_utc": datetime.utcnow(),
            "success": False,
            "status_code": None,
            "error": None,
        }
        try:
            logging.info(f"Fetching weather data from {WEATHER_URL} (Attempt {attempt_num + 1}/{MAX_RETRIES})")
            response = requests.get(WEATHER_URL, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            
            attempt_info["success"] = True
            attempt_info["status_code"] = response.status_code
            attempts_log.append(attempt_info)
            logging.info("Successfully fetched weather data.")
            return response.json(), attempts_log
        except requests.exceptions.Timeout:
            attempt_info["error"] = "Request timed out"
            attempts_log.append(attempt_info)
            logging.warning(f"Request timed out. Retrying in {RETRY_DELAY_SECONDS} seconds...")
            time.sleep(RETRY_DELAY_SECONDS)
        except requests.exceptions.RequestException as e:
            attempt_info["error"] = str(e)
            attempts_log.append(attempt_info)
            logging.error(f"An error occurred during the request: {e}. Retrying in {RETRY_DELAY_SECONDS} seconds...")
            time.sleep(RETRY_DELAY_SECONDS)

    logging.error("Failed to fetch weather data after several attempts.")
    return None, attempts_log

def weather_job(client):
    """
    The main job to be scheduled. Fetches weather and saves it to MongoDB.
    """
    weather_data, attempts_log = fetch_weather_data()
    if client:
        db = client.weather_db
        attempts_collection = db.attempts
        hourly_reports_collection = db.hourly_reports

        # Save the attempts log
        if attempts_log:
            attempts_collection.insert_many(attempts_log)
            logging.info("Successfully saved attempt log to MongoDB.")

        # If weather data is fetched successfully, process and save it
        if weather_data:
            try:
                for daily_weather in weather_data.get("weather", []):
                    report_date = daily_weather.get("date")
                    if report_date:
                        # Create a record with the date and the hourly data
                        record = {
                            "date": report_date,
                            "hourly": daily_weather.get("hourly", []),
                            "timestamp_recorded_utc": datetime.utcnow()
                        }
                        # Use update_one with upsert=True to overwrite or create
                        hourly_reports_collection.update_one(
                            {"date": report_date},
                            {"$set": record},
                            upsert=True
                        )
                        logging.info(f"Successfully upserted hourly data for {report_date}.")
            except Exception as e:
                logging.error(f"Failed to write weather data to MongoDB: {e}")

def main():
    """
    Main function to initialize the client and start the scheduler.
    """
    mongo_client = get_mongo_client()

    if not mongo_client:
        return # Exit if we can't connect to the database

    # --- Scheduler Setup ---
    logging.info("Scheduler started. First job will run in the next hour.")
    schedule.every().hour.do(weather_job, client=mongo_client)
    
    # Run the job once immediately on startup
    logging.info("Performing initial weather data fetch...")
    weather_job(mongo_client)
    logging.info("Initial fetch complete. Waiting for next scheduled run...")

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()