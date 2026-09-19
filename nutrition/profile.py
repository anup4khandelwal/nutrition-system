import json
from dataclasses import dataclass

@dataclass
class Profile:
    diet_type: str
    eggs: bool
    cuisines: list
    meals_per_day: int
    dislikes: list
    flags: dict
    targets: dict
    emphasize_foods: list
    supplements: list

def load_profile(path: str) -> Profile:
    with open(path) as f:
        raw = json.load(f)
    if "targets" not in raw or "diet" not in raw:
        raise ValueError("profile must contain 'diet' and 'targets'")
    diet = raw["diet"]
    return Profile(
        diet_type=diet["type"],
        eggs=diet.get("eggs", False),
        cuisines=diet.get("cuisines", []),
        meals_per_day=diet.get("meals_per_day", 3),
        dislikes=diet.get("dislikes", []),
        flags=raw.get("flags", {}),
        targets=raw["targets"],
        emphasize_foods=raw.get("emphasize_foods", []),
        supplements=raw.get("supplements", []),
    )
