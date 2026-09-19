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

from urllib.parse import quote_plus

def _blinkit_link(item: str) -> str:
    return f"https://blinkit.com/s/?q={quote_plus(item)}"

def build_checklist(agg: list, supplements: list, week_no: int) -> str:
    lines = [f"# Blinkit Grocery Checklist — Week {week_no}", "",
             "_Tap each link, add to cart on Blinkit, then sign in & pay._", "",
             "## Groceries"]
    for row in agg:
        lines.append(f"- [ ] {row['item']} (x{row['count']}) — [add]({_blinkit_link(row['item'])})")
    lines += ["", "## Supplements (confirm dose with your doctor)"]
    for s in supplements:
        lines.append(f"- [ ] {s['name']} — [add]({_blinkit_link(s['name'])})  _{s.get('note','')}_")
    return "\n".join(lines)
