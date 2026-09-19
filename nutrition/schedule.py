from datetime import date

def day_index(start: date, today: date) -> int:
    delta = (today - start).days
    return (delta % 30) + 1

def todays_meals(meal_plan, start: date, today: date) -> dict:
    idx = day_index(start, today)
    d = meal_plan.days[idx - 1]
    return {"breakfast": d["breakfast"], "lunch": d["lunch"], "dinner": d["dinner"]}
