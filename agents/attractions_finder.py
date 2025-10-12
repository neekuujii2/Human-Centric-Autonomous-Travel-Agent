# agents/nearby_attractions/attractions_finder.py

import requests

def get_attractions(destination):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{destination}"
        res = requests.get(url).json()
        summary = res.get("extract", "No information found.")
        return {"nearby_attractions": f"🏛️ **Top Attractions in {destination}:**\n{summary}"}
    except Exception as e:
        return {"nearby_attractions": f"Failed to fetch attractions: {e}"}
