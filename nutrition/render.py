from nutrition.mealplan import MealPlan, MEALS

def render_markdown(mp: MealPlan) -> str:
    lines = ["# 30-Day Meal Plan", ""]
    for d in mp.days:
        lines.append(f"## Day {d['day']}")
        for meal in MEALS:
            lines.append(f"- **{meal.title()}:** {d[meal]['dish']}")
        lines.append("")
    return "\n".join(lines)
