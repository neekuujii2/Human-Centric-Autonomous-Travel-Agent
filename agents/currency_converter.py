import requests

# Simple location to currency mapping
CITY_TO_CURRENCY = {
    "new york": "USD",
    "los angeles": "USD",
    "san francisco": "USD",
    "paris": "EUR",
    "tokyo": "JPY",
    "london": "GBP",
    "delhi": "INR",
    "mumbai": "INR",
    "bangkok": "THB",
    "dubai": "AED",
    "sydney": "AUD",
    "toronto": "CAD"
    # aur cities add kar sakte ho
}

def get_currency_from_city(city_name):
    city = city_name.lower().strip()
    return CITY_TO_CURRENCY.get(city, "USD")  # default USD if not found

def convert_currency(amount=1, from_currency="USD", to_currency="INR"):
    try:
        url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount={amount}"
        res = requests.get(url).json()

        if "result" in res and res["result"] is not None:
            converted = res["result"]
            return f"💱 {amount} {from_currency} = {converted:.2f} {to_currency}"
        else:
            return "⚠️ Currency conversion failed or rate not available."
    except Exception as e:
        return f"❌ Error in conversion: {e}"

def get_currency_info(state):
    from_city = state.get("from", "New York")
    to_city = state.get("destination", "Paris")

    from_currency = get_currency_from_city(from_city)
    to_currency = get_currency_from_city(to_city)

    return {
        "currency_info": convert_currency(1, from_currency, to_currency)
    }
