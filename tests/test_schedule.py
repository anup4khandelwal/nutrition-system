from datetime import date
from nutrition.schedule import day_index, todays_meals

START = date(2026, 9, 22)

def test_day_index_wraps_over_30():
    assert day_index(START, START) == 1
    assert day_index(START, date(2026, 10, 21)) == 30
    assert day_index(START, date(2026, 10, 22)) == 1

def test_todays_meals_returns_three(tmp_path):
    import json
    plan = {"days": [{"day": i, "breakfast": {"dish": f"b{i}", "ingredients": []},
                      "lunch": {"dish": f"l{i}", "ingredients": []},
                      "dinner": {"dish": f"d{i}", "ingredients": []}} for i in range(1, 31)]}
    f = tmp_path / "mp.json"; f.write_text(json.dumps(plan))
    from nutrition.mealplan import load_meal_plan
    mp = load_meal_plan(str(f))
    meals = todays_meals(mp, START, START)
    assert meals["breakfast"]["dish"] == "b1"
