import json, pytest
from nutrition.mealplan import load_meal_plan, MealPlan

def _sample(tmp_path, days=30):
    plan = {"days": []}
    for d in range(1, days + 1):
        plan["days"].append({
            "day": d,
            "breakfast": {"dish": "Vegetable oats upma",
                          "ingredients": [{"item": "oats", "qty": "50 g"}]},
            "lunch": {"dish": "Rajma with brown rice",
                      "ingredients": [{"item": "rajma", "qty": "60 g"}]},
            "dinner": {"dish": "Palak paneer with roti",
                       "ingredients": [{"item": "spinach", "qty": "150 g"}]},
        })
    f = tmp_path / "mp.json"
    f.write_text(json.dumps(plan))
    return str(f)

def test_load_meal_plan_ok(tmp_path):
    mp = load_meal_plan(_sample(tmp_path))
    assert isinstance(mp, MealPlan)
    assert len(mp.days) == 30
    assert mp.days[0]["breakfast"]["dish"] == "Vegetable oats upma"

def test_load_meal_plan_requires_30_days(tmp_path):
    with pytest.raises(ValueError):
        load_meal_plan(_sample(tmp_path, days=29))

def test_load_meal_plan_requires_three_meals(tmp_path):
    bad = {"days": [{"day": 1, "breakfast": {"dish": "x", "ingredients": []}}]}
    f = tmp_path / "bad.json"; f.write_text(json.dumps(bad))
    with pytest.raises(ValueError):
        load_meal_plan(str(f))
