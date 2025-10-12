# agents/festival_event_finder.py
import requests
from datetime import datetime
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
PREDICTHQ_TOKEN = os.getenv("PREDICTHQ_TOKEN")
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
EVENTBRITE_API_KEY = os.getenv("EVENTBRITE_API_KEY")
GOOGLE_CALENDAR_API_KEY = os.getenv("GOOGLE_API_KEY")

def format_date_utc(date_str: str, start: bool = True) -> str:
    """Convert to UTC format required by APIs"""
    return f"{date_str}T00:00:00Z" if start else f"{date_str}T23:59:59Z"

# ------------------- PredictHQ -------------------
def fetch_predicthq_events(city: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    if not PREDICTHQ_TOKEN:
        return []
    url = "https://api.predicthq.com/v1/events/"
    headers = {"Authorization": f"Bearer {PREDICTHQ_TOKEN}"}
    params = {
        "q": city,
        "start.gte": start_date,
        "start.lte": end_date,
        "limit": 20,
    }
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        events = []
        for e in r.json().get("results", []):
            events.append({
                "name": e.get("title"),
                "date": e.get("start")[:10],
                "time": e.get("start")[11:16] if "T" in e.get("start") else None,
                "venue": e.get("entities", [{}])[0].get("name"),
                "url": e.get("url"),
                "source": "PredictHQ"
            })
        return events
    except Exception as ex:
        print("PredictHQ Error:", ex)
        return []

# ------------------- Ticketmaster -------------------
def fetch_ticketmaster_events(city: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    if not TICKETMASTER_API_KEY:
        return []
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "city": city,
        "startDateTime": format_date_utc(start_date, True),
        "endDateTime": format_date_utc(end_date, False),
        "apikey": TICKETMASTER_API_KEY,
        "size": 20,
        "sort": "date,asc"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        events = []
        for e in r.json().get("_embedded", {}).get("events", []):
            events.append({
                "name": e.get("name"),
                "date": e.get("dates", {}).get("start", {}).get("localDate"),
                "time": e.get("dates", {}).get("start", {}).get("localTime"),
                "venue": e.get("_embedded", {}).get("venues", [{}])[0].get("name"),
                "url": e.get("url"),
                "source": "Ticketmaster"
            })
        return events
    except Exception as ex:
        print("Ticketmaster Error:", ex)
        return []

# ------------------- Eventbrite -------------------
def fetch_eventbrite_events(city: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    if not EVENTBRITE_API_KEY:
        return []
    
    url = "https://www.eventbriteapi.com/v3/events/search/"
    headers = {"Authorization": f"Bearer {EVENTBRITE_API_KEY}"}
    params = {
        "location.address": city,
        "start_date.range_start": format_date_utc(start_date, True),
        "start_date.range_end": format_date_utc(end_date, False),
        "page": 1,
    }
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code == 404:  # Fallback: try keyword search
            params = {
                "q": city,
                "start_date.range_start": format_date_utc(start_date, True),
                "start_date.range_end": format_date_utc(end_date, False),
                "page": 1,
            }
            r = requests.get(url, headers=headers, params=params, timeout=10)

        r.raise_for_status()
        events = []
        for e in r.json().get("events", []):
            events.append({
                "name": e.get("name", {}).get("text"),
                "date": e.get("start", {}).get("local")[:10] if e.get("start", {}).get("local") else None,
                "time": e.get("start", {}).get("local")[11:16] if e.get("start", {}).get("local") else None,
                "venue": None,
                "url": e.get("url"),
                "source": "Eventbrite"
            })
        return events
    except Exception as ex:
        print("Eventbrite Error:", ex)
        return []


# ------------------- Indian Festivals (Google Calendar) -------------------
def fetch_indian_festivals(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    if not GOOGLE_CALENDAR_API_KEY:
        return []
    url = f"https://www.googleapis.com/calendar/v3/calendars/en.indian%23holiday%40group.v.calendar.google.com/events"
    params = {
        "key": GOOGLE_CALENDAR_API_KEY,
        "timeMin": format_date_utc(start_date, True),
        "timeMax": format_date_utc(end_date, False),
        "singleEvents": True,
        "orderBy": "startTime"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        events = []
        for e in r.json().get("items", []):
            events.append({
                "name": e.get("summary"),
                "date": e.get("start", {}).get("date"),
                "time": None,
                "venue": "India (National Festival)",
                "url": None,
                "source": "Indian Festivals (Google Calendar)"
            })
        return events
    except Exception as ex:
        print("Indian Festival Error:", ex)
        return []

# ------------------- Master Fetch -------------------
def fetch_festivals_and_events(city: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Fetch events from available APIs in priority order"""
    events = []

    # Priority: PredictHQ > Ticketmaster > Eventbrite
    events.extend(fetch_predicthq_events(city, start_date, end_date))
    if not events:
        events.extend(fetch_ticketmaster_events(city, start_date, end_date))
    if not events:
        events.extend(fetch_eventbrite_events(city, start_date, end_date))

    # Always add Indian festivals if city is in India
    if city.lower() in ["delhi", "mumbai", "bangalore", "kolkata", "chennai", "jaipur", "varanasi", "india"]:
        events.extend(fetch_indian_festivals(start_date, end_date))

    # sort by date
    events.sort(key=lambda x: (x["date"] or "9999-12-31"))
    return events
