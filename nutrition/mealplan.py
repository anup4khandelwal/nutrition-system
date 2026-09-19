import json
from dataclasses import dataclass

MEALS = ("breakfast", "lunch", "dinner")

@dataclass
class MealPlan:
    days: list

def load_meal_plan(path: str) -> MealPlan:
    with open(path) as f:
        raw = json.load(f)
    days = raw.get("days", [])
    if len(days) != 30:
        raise ValueError(f"meal plan must have 30 days, got {len(days)}")
    for d in days:
        for meal in MEALS:
            if meal not in d or "dish" not in d[meal]:
                raise ValueError(f"day {d.get('day')} missing {meal}.dish")
            d[meal].setdefault("ingredients", [])
    return MealPlan(days=days)

def all_dishes(mp: MealPlan) -> list:
    names = []
    for d in mp.days:
        for meal in MEALS:
            names.append(d[meal]["dish"])
    seen, out = set(), []
    for n in names:
        if n not in seen:
            seen.add(n); out.append(n)
    return out
