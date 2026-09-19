from nutrition.grocery import aggregate_week

def _week_meals():
    days = []
    for i in range(7):
        days.append({
            "breakfast": {"dish": "b", "ingredients": [{"item": "oats", "qty": "50 g"}]},
            "lunch": {"dish": "l", "ingredients": [{"item": "rajma", "qty": "60 g"}]},
            "dinner": {"dish": "d", "ingredients": [{"item": "spinach", "qty": "150 g"}]},
        })
    return days

def test_aggregate_counts_occurrences():
    agg = aggregate_week(_week_meals())
    items = {row["item"]: row for row in agg}
    assert items["oats"]["count"] == 7
    assert items["rajma"]["count"] == 7
    assert "50 g" in items["oats"]["quantities"]
