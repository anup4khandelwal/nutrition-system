from nutrition.mealplan import MEALS

def aggregate_week(days: list) -> list:
    agg = {}
    for d in days:
        for meal in MEALS:
            for ing in d[meal].get("ingredients", []):
                item = ing["item"].strip().lower()
                rec = agg.setdefault(item, {"item": item, "count": 0, "quantities": []})
                rec["count"] += 1
                rec["quantities"].append(ing.get("qty", ""))
    return sorted(agg.values(), key=lambda r: r["item"])
