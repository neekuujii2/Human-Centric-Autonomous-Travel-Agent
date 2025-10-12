import os
import requests
from dotenv import load_dotenv
from agents.hotel_finder import get_city_coords, fetch_place_details

load_dotenv()
OPENTRIPMAP_KEY = os.getenv("OPENTRIPMAP_KEY")

def get_cuisines(city, radius=5000, limit=10, cuisine_filter=None):
    """Fetch restaurants in a city with optional cuisine filter"""
    lat, lon = get_city_coords(city)
    if not lat:
        return []
    url = "https://api.opentripmap.com/0.1/en/places/radius"
    params = {
        "radius": radius,
        "lon": lon,
        "lat": lat,
        "kinds": "restaurants",
        "limit": limit,
        "apikey": OPENTRIPMAP_KEY
    }
    res = requests.get(url, params=params)
    results = []
    if res.status_code == 200:
        for place in res.json().get("features", []):
            xid = place["properties"].get("xid")
            details = fetch_place_details(xid)
            if cuisine_filter:
                if cuisine_filter.lower() in details.get("name", "").lower():
                    results.append(details)
            else:
                results.append(details)
    return results
