import json, sys
from datetime import date
from nutrition.mealplan import load_meal_plan
from nutrition.schedule import todays_meals

START = date(2026, 9, 22)

def main():
    mp = load_meal_plan("data/meal_plan.json")
    videos = json.load(open("data/videos.json"))
    meals = todays_meals(mp, START, date.today())
    payload = {"meals": {}}
    for meal, info in meals.items():
        dish = info["dish"]
        v = videos.get(dish)
        payload["meals"][meal] = {"dish": dish, "video": v}
    json.dump(payload, open("data/today.json", "w"), indent=2)
    print("wrote data/today.json")

if __name__ == "__main__":
    sys.exit(main())
