import json
from datetime import date
from nutrition.mealplan import load_meal_plan
from nutrition.profile import load_profile
from nutrition.schedule import day_index
from nutrition.grocery import aggregate_week, build_checklist

START = date(2026, 9, 22)

def next_week_days(mp, start, today):
    idx = day_index(start, today)
    out = []
    for k in range(7):
        di = ((idx - 1 + k) % 30)
        out.append(mp.days[di])
    return out, ((idx - 1)//7) + 1

def main():
    mp = load_meal_plan("data/meal_plan.json")
    prof = load_profile("data/profile.json")
    days, week_no = next_week_days(mp, START, date.today())
    agg = aggregate_week(days)
    json.dump(agg, open(f"data/grocery_week_{week_no}.json", "w"), indent=2)
    md = build_checklist(agg, prof.supplements, week_no)
    open(f"data/grocery_week_{week_no}.md", "w").write(md)
    print(f"wrote data/grocery_week_{week_no}.md")

if __name__ == "__main__":
    main()
