#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
import os
import logging
import json
from pytz import timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_BASE_URL = os.getenv("API_URL", "http://api:8000")

def format_time_hhmm(t):
    """Convert numeric HHMM (e.g., 900, 1200) to 'H:MM am/pm'."""
    try:
        ti = int(t)
    except (TypeError, ValueError):
        return str(t)
    hour = ti // 100
    minute = ti % 100
    # ampm = 'am' if hour < 12 else 'pm'
    hour12 = hour % 12
    if hour12 == 0:
        hour12 = 12
    return f"{hour12}:{minute:02d}"

def get_weather_for_date(date_str):
    """Fetches weather from the API for a specific date."""
    try:
        response = requests.get(f"{API_BASE_URL}/weather/{date_str}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching weather for {date_str}: {e}")
        return None

def daily_weather_alert():
    """Scheduled job to get and log weather for today and tomorrow."""
    logging.info("Executing daily weather alert job...")
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    wind_threshold = int(os.getenv("WINDSPEED_ThRESHOLD", "15"))
    cuttoff_time = 900

    hourly_wind_today = []
    hourly_wind_tomorrow = []

    logging.info(f"--- Weather for {today} ---")
    weather_today = get_weather_for_date(today)
    if weather_today and 'hourly' in weather_today:
        hourly_wind_today = [{'time': h['time'], 'windspeed': h['windspeedMiles']} for h in weather_today['hourly'] if int(h['time']) >= cuttoff_time]

    logging.info(f"--- Weather for {tomorrow} ---")
    weather_tomorrow = get_weather_for_date(tomorrow)
    if weather_tomorrow and 'hourly' in weather_tomorrow:
        hourly_wind_tomorrow = [{'time': h['time'], 'windspeed': h['windspeedMiles']} for h in weather_tomorrow['hourly'] if int(h['time']) < cuttoff_time]
    
    hourly_winds = hourly_wind_today + hourly_wind_tomorrow
    filtered_winds = [h for h in hourly_winds if int(h['windspeed']) >= wind_threshold]

    logging.info("--- Filtered Weather ---")
    logging.info(filtered_winds)

    if len(filtered_winds) == 0:
        logging.info('No high winds today')
        return
    
    # raw numeric times from API (e.g. 900, 1200)
    start_time = filtered_winds[0]['time']
    last_checked_time = hourly_winds[-1]['time']
    last_high_wind_time = filtered_winds[-1]['time']
    start_time_fmt = format_time_hhmm(start_time)
    end_time_fmt = format_time_hhmm(last_high_wind_time)
    max_speed = max(int(h['windspeed']) for h in filtered_winds)

    body = "Unknown wind notification"
    if last_checked_time == last_high_wind_time:
        body = f"High winds starting at {start_time_fmt} and continuing into tomorrow, with gusts up to {max_speed}mph."
    else:
        if start_time == last_high_wind_time:
            body = f"High winds of {max_speed}mph expected around {start_time_fmt}."
        else:
            body = f"High winds expected from {start_time_fmt} to {end_time_fmt}, with gusts up to {max_speed}mph."

    if len(filtered_winds) == 1:
        end_time_fmt = format_time_hhmm(last_high_wind_time + 100)
    
    logging.info(body)

    payload = {
        "title": "Batten Down the Decorations!",
        "body": body,
        "data": {
            "actions": json.dumps([
                {"action": "add-wind-task", "title": "Yes"},
                {"action": "dismiss", "title": "No"}
            ]),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "body": body,
            "startHour": start_time_fmt,
            "endHour": end_time_fmt
        }
    }
    REGION = os.getenv("REGION", "us-central1")
    PROJECT = os.getenv("PROJECT", "taskr-1428")
    FUNCTION = os.getenv("FUNCTION", "sendMessage")
    USER_ID = os.getenv("USER_ID", "493KKO1BmXca1bRUVwa0PY6HzzT2")
    try:
        resp = requests.post(
            f"https://{REGION}-{PROJECT}.cloudfunctions.net/{FUNCTION}",
            json={"userId": USER_ID, "payload": payload},
            timeout=10
        )
        resp.raise_for_status()
        logging.info(f"Notification sent successfully: {resp.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending notification: {e}")

    logging.info("Daily weather alert job finished.")

if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone=timezone('America/New_York'))
    # Schedule the job to run every day at 10:00 EST, with grace time to run even if missed
    alert_cron_hour = int(os.getenv("ALERT_CRON_HOUR", "10"))
    alert_cron_minute = int(os.getenv("ALERT_CRON_MINUTE", "0"))
    scheduler.add_job(daily_weather_alert, 'cron', hour=alert_cron_hour, minute=alert_cron_minute, misfire_grace_time=24*3600, coalesce=True)

    logging.info(f"Scheduler started. Waiting for the next scheduled run at {alert_cron_hour:02d}:{alert_cron_minute:02d} AM.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass