import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
serpapi_key = os.getenv("SERPAPI_KEY")

# Simple IATA mapping
iata_codes = {
    "NEW DELHI": "DEL",
    "DELHI": "DEL",
    "MUMBAI": "BOM",
    "BOMBAY": "BOM",
    "CHENNAI": "MAA",
    "BANGALORE": "BLR",
    "KOLKATA": "CCU",
    "HYDERABAD": "HYD",
    "GOA": "GOI",
    "JAIPUR": "JAI",
    "AHMEDABAD": "AMD",
    "KOCHI": "COK",
    "PUNE": "PNQ",
    "LUCKNOW": "LKO"
}

def city_to_iata(city):
    city_upper = city.strip().upper()
    return iata_codes.get(city_upper, city_upper if len(city_upper) == 3 else city)

def minutes_to_hours_mins(minutes):
    """Convert minutes to Hh Mm format."""
    try:
        minutes = int(minutes)
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m" if hours else f"{mins}m"
    except:
        return "N/A"
    
def extract_duration(flight, segments):
    """Extract duration with multiple fallbacks."""
    # Try direct fields
    if flight.get("total_duration_in_minutes"):
        return minutes_to_hours_mins(flight["total_duration_in_minutes"])
    if flight.get("total_duration"):
        return minutes_to_hours_mins(flight["total_duration"])
    
    # Try segment-based duration
    if segments:
        seg_duration = segments[0].get("duration") or segments[0].get("duration_in_minutes")
        if seg_duration:
            return minutes_to_hours_mins(seg_duration)
    
    # Absolute fallback: calculate from times
    try:
        from datetime import datetime
        dep_time_str = segments[0].get("departure_airport", {}).get("time") or segments[0].get("departure_time")
        arr_time_str = segments[-1].get("arrival_airport", {}).get("time") or segments[-1].get("arrival_time")
        if dep_time_str and arr_time_str:
            dep_time = datetime.fromisoformat(dep_time_str.replace("Z", "+00:00"))
            arr_time = datetime.fromisoformat(arr_time_str.replace("Z", "+00:00"))
            mins = int((arr_time - dep_time).total_seconds() / 60)
            return minutes_to_hours_mins(mins)
    except:
        pass
    
    return "N/A"


def search_one_way_flights(departure, arrival, depart_date, adults=1, currency="INR"):
    if not serpapi_key:
        print("❌ SERPAPI_KEY not found")
        return []

    departure_id = city_to_iata(departure)
    arrival_id = city_to_iata(arrival)

    try:
        if isinstance(depart_date, str):
            date_obj = datetime.strptime(depart_date, "%Y-%m-%d")
        else:
            date_obj = depart_date
        formatted_date = date_obj.strftime("%Y-%m-%d")
    except:
        formatted_date = str(depart_date)

    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": formatted_date,
        "adults": str(adults),
        "currency": currency,
        "hl": "en",
        "gl": "in",
        "type": 2,  # Force one-way
        "api_key": serpapi_key
    }

    print(f"🔍 Searching: {departure_id} → {arrival_id} on {formatted_date}")

    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=30)
        if response.status_code != 200:
            print(f"❌ HTTP Error {response.status_code}: {response.text[:200]}")
            return []

        result = response.json()
        if "error" in result:
            print(f"❌ API Error: {result['error']}")
            return []

        flights = []
        for key in ["best_flights", "other_flights", "flights"]:
            flights.extend(result.get(key, []))

        if not flights:
            print("❌ No flights found")
            return []

        formatted_flights = []
        for flight in flights[:8]:
            try:
                # Price formatting
                price = flight.get("price", "N/A")
                if isinstance(price, (int, float)):
                    price = f"₹{price:,}"

                # Segments extraction
                flight_segments = flight.get("flights") or flight.get("segments", [])
                if not flight_segments:
                    continue

                main_segment = flight_segments[0]
                last_segment = flight_segments[-1]

                # Time extraction with multiple fallback options
                dep_time = (
                    main_segment.get("departure_airport", {}).get("time")
                    or main_segment.get("departure_time")
                    or "N/A"
                )
                arr_time = (
                    last_segment.get("arrival_airport", {}).get("time")
                    or last_segment.get("arrival_time")
                    or "N/A"
                )

                # Duration formatting
                duration = extract_duration(flight, flight_segments)

                formatted_flights.append({
                    "airline": main_segment.get("airline", "Unknown"),
                    "flight_number": main_segment.get("flight_number", "N/A"),
                    "departure_time": dep_time,
                    "arrival_time": arr_time,
                    "duration_mins": duration,
                    "price": price,
                    "agent": "Google Flights"
                })
            except Exception as e:
                print(f"⚠ Error processing flight: {e}")
                continue

        return formatted_flights
    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return []

def get_sample_flights(departure, arrival, depart_date, adults=1):
    print("🔄 Providing sample flight data...")
    return [
        {"airline": "IndiGo", "flight_number": "6E-345", "departure_time": f"{depart_date} 08:30",
         "arrival_time": f"{depart_date} 10:45", "duration_mins": "2h 15m", "price": "₹4,850",
         "agent": "Multiple booking sites"},
        {"airline": "SpiceJet", "flight_number": "SG-128", "departure_time": f"{depart_date} 14:20",
         "arrival_time": f"{depart_date} 16:35", "duration_mins": "2h 15m", "price": "₹4,200",
         "agent": "Multiple booking sites"},
        {"airline": "Air India", "flight_number": "AI-502", "departure_time": f"{depart_date} 18:15",
         "arrival_time": f"{depart_date} 20:30", "duration_mins": "2h 15m", "price": "₹5,650",
         "agent": "Multiple booking sites"}
    ]

def search_flights_with_fallback(departure, arrival, depart_date, adults=1, currency="INR"):
    print(f"🛫 Searching flights: {departure} → {arrival}")
    flights = search_one_way_flights(departure, arrival, depart_date, adults, currency)
    if not flights:
        flights = get_sample_flights(departure, arrival, depart_date, adults)
    return flights

if __name__ == "__main__":
    test_flights = search_flights_with_fallback("New Delhi", "Mumbai", "2025-08-15", 1)
    print(f"✅ Found {len(test_flights)} flights")
    for f in test_flights:
        print(f)
