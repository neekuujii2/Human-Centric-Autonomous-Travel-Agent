# agents/budget_estimator/budget_estimator.py

def estimate_budget(state):
    duration = state["preferences"].get("duration", 7)
    budget_type = state["preferences"].get("budget_type", "Mid-Range")
    num_people = state["preferences"].get("num_people", "1")

    # Basic USD per day cost
    rates = {
        "Budget": 30,
        "Backpacker": 40,
        "Mid-Range": 60,
        "Family": 80,
        "Luxury": 150
    }
    cost_per_day = rates.get(budget_type, 60)

    people_count = 1
    if num_people == "2":
        people_count = 2
    elif num_people == "3":
        people_count = 3
    elif num_people == "4-6":
        people_count = 5
    elif num_people == "7-10":
        people_count = 8
    elif num_people == "10+":
        people_count = 12

    total = duration * cost_per_day * people_count
    return {"estimated_budget": f"💰 Estimated Total Budget: **${total} USD** for {people_count} people and {duration} days."}
