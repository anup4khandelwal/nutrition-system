# Automated Personalized Nutrition System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Mac-hosted system that turns Anup's blood-report findings into a 30-day Indian-vegetarian meal plan, pairs each dish with a YouTube recipe video sent to his cook via WhatsApp daily, and produces a weekly Blinkit grocery checklist he pays for himself.

**Architecture:** A Python package (`nutrition/`) owns the data model, meal-plan engine, YouTube matcher, and grocery builder, writing JSON artifacts into `data/`. A small Node script (`whatsapp/`) uses `whatsapp-web.js` to send the daily video. macOS `launchd` triggers the daily send and the weekly grocery build. All state lives in flat JSON files — no database.

**Tech Stack:** Python 3.11+ (pytest, requests, python-dotenv), Node 18+ (`whatsapp-web.js`, `qrcode-terminal`), YouTube Data API v3, macOS `launchd`.

---

## Reference: Spec

Full design at `docs/superpowers/specs/2026-09-19-nutrition-system-design.md`. Key locked decisions:
- Grocery = Blinkit, approach **B2** (checklist + deep links; Anup pays).
- WhatsApp = **W3** (`whatsapp-web.js`) + `wa.me` fallback; fully autonomous daily **7:30 AM**.
- Weekly grocery list generated **Sunday evening**.
- Meal brief: Indian veg (lacto, **no eggs**), N+S mix, 3 meals/day, cook skilled, no dislikes; **heart-healthy (low LDL), high soluble fiber, B12- & Vitamin-D-conscious**.
- Report flags: B12 <148 (deficient), Vit D 14.1 (deficient), LDL 127 (high), Non-HDL 153 (high), HDL 41 (low-ish).

---

## File Structure

```
nutrition-system/
├── pyproject.toml                 # Python project + deps + pytest config
├── .env.example                   # YOUTUBE_API_KEY, COOK_WHATSAPP
├── nutrition/
│   ├── __init__.py
│   ├── profile.py                 # load/validate profile.json; nutrient targets
│   ├── mealplan.py                # 30-day plan model + loader/validator
│   ├── youtube.py                 # YouTube Data API search + cache
│   ├── grocery.py                 # aggregate week -> categorized list
│   ├── schedule.py                # "today's meal", "next week's meals" helpers
│   └── render.py                  # meal_plan.json -> readable Markdown
├── data/
│   ├── profile.json               # authored in Phase 0
│   ├── meal_plan.json             # authored in Phase 1, validated by code
│   ├── videos.json                # produced in Phase 2
│   └── grocery_week_N.json        # produced in Phase 4
├── whatsapp/
│   ├── package.json
│   ├── send.js                    # sends today's video via whatsapp-web.js
│   └── message.js                 # pure fn: build message text (unit-testable)
├── scripts/
│   ├── run_daily.sh               # calls python (pick video) + node send.js
│   └── run_weekly.sh              # calls python grocery build + checklist
├── launchd/
│   ├── com.anup.nutrition.daily.plist
│   └── com.anup.nutrition.weekly.plist
└── tests/
    ├── test_profile.py
    ├── test_mealplan.py
    ├── test_youtube.py
    ├── test_grocery.py
    ├── test_schedule.py
    └── test_message.mjs
```

---

## PHASE 0 — Project Setup & Profile

### Task 0.1: Python project skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `nutrition/__init__.py`
- Create: `.env.example`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "nutrition-system"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["requests>=2.31", "python-dotenv>=1.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

- [ ] **Step 2: Create `nutrition/__init__.py`** (empty marker)

```python
"""Nutrition system package."""
```

- [ ] **Step 3: Create `.env.example`**

```bash
YOUTUBE_API_KEY=your_key_here
COOK_WHATSAPP=+91XXXXXXXXXX
```

- [ ] **Step 4: Create venv & install**

Run:
```bash
cd ~/nutrition-system && python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"
```
Expected: installs requests, python-dotenv, pytest without error.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml nutrition/__init__.py .env.example
git commit -m "chore: python project skeleton"
```

### Task 0.2: Author `data/profile.json`

**Files:**
- Create: `data/profile.json`

- [ ] **Step 1: Write the profile from the report**

```json
{
  "person": { "name": "Anup", "age": 42, "sex": "male" },
  "diet": {
    "type": "lacto-vegetarian",
    "eggs": false,
    "cuisines": ["north-indian", "south-indian"],
    "meals_per_day": 3,
    "dislikes": []
  },
  "flags": {
    "vitamin_b12_deficient": true,
    "vitamin_d_deficient": true,
    "ldl_high": true,
    "non_hdl_high": true,
    "hdl_low": true
  },
  "targets": {
    "calories_kcal": 2200,
    "protein_g": 75,
    "fiber_g": 35,
    "soluble_fiber_g": 10,
    "saturated_fat_max_g": 15,
    "added_sugar_max_g": 25
  },
  "emphasize_foods": [
    "oats", "barley", "flax", "legumes", "leafy-greens",
    "curd", "paneer", "fortified-milk", "nuts", "soy"
  ],
  "supplements": [
    { "name": "Vitamin B12 (methylcobalamin)", "note": "doctor to confirm dose" },
    { "name": "Vitamin D3", "note": "doctor to confirm dose" },
    { "name": "Omega-3 (algal, vegetarian)", "note": "500-1000mg EPA+DHA/day" }
  ]
}
```

- [ ] **Step 2: Commit**

```bash
git add data/profile.json
git commit -m "feat: author profile from blood report"
```

### Task 0.3: Profile loader with validation (TDD)

**Files:**
- Create: `nutrition/profile.py`
- Test: `tests/test_profile.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_profile.py
from nutrition.profile import load_profile, Profile

def test_load_profile_reads_targets_and_flags():
    p = load_profile("data/profile.json")
    assert isinstance(p, Profile)
    assert p.diet_type == "lacto-vegetarian"
    assert p.eggs is False
    assert p.targets["fiber_g"] == 35
    assert p.flags["ldl_high"] is True
    assert "Vitamin B12 (methylcobalamin)" in [s["name"] for s in p.supplements]

def test_load_profile_rejects_missing_targets(tmp_path):
    import json, pytest
    bad = tmp_path / "p.json"
    bad.write_text(json.dumps({"diet": {"type": "x"}}))
    with pytest.raises(ValueError):
        load_profile(str(bad))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_profile.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'nutrition.profile'`.

- [ ] **Step 3: Write minimal implementation**

```python
# nutrition/profile.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_profile.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add nutrition/profile.py tests/test_profile.py
git commit -m "feat: profile loader with validation"
```

---

## PHASE 1 — Meal Plan Engine

The 30-day plan JSON is **authored by Goose (LLM) once** against the profile, then the code
validates it and renders it to Markdown for Anup to review. Code enforces correctness; the
LLM supplies the culinary content.

### Task 1.1: Meal-plan data model + validator (TDD)

**Files:**
- Create: `nutrition/mealplan.py`
- Test: `tests/test_mealplan.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_mealplan.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_mealplan.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'nutrition.mealplan'`.

- [ ] **Step 3: Write minimal implementation**

```python
# nutrition/mealplan.py
import json
from dataclasses import dataclass

MEALS = ("breakfast", "lunch", "dinner")

@dataclass
class MealPlan:
    days: list  # list of dicts with day, breakfast, lunch, dinner

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
    # de-dup preserving order
    seen, out = set(), []
    for n in names:
        if n not in seen:
            seen.add(n); out.append(n)
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_mealplan.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add nutrition/mealplan.py tests/test_mealplan.py
git commit -m "feat: meal plan model + validator"
```

### Task 1.2: Author `data/meal_plan.json` (LLM content, human-reviewed)

**Files:**
- Create: `data/meal_plan.json`

- [ ] **Step 1: Generate the 30-day plan**

Goose authors `data/meal_plan.json` following the profile brief. Each of 30 days has
`breakfast`, `lunch`, `dinner`, each with `dish` and `ingredients:[{item, qty}]`. Rules:
no eggs; emphasize oats/barley/flax/legumes/leafy-greens/curd/paneer/fortified-milk/nuts/soy;
limit fried/ghee-heavy items; rotate N & S Indian dishes; no repeats within any 5-day window.

- [ ] **Step 2: Validate it with the Phase 1.1 loader**

Run:
```bash
python3 -c "from nutrition.mealplan import load_meal_plan, all_dishes; mp=load_meal_plan('data/meal_plan.json'); print('days', len(mp.days), 'unique dishes', len(all_dishes(mp)))"
```
Expected: prints `days 30 unique dishes <N>` with no exception.

- [ ] **Step 3: Commit**

```bash
git add data/meal_plan.json
git commit -m "feat: author 30-day meal plan"
```

### Task 1.3: Render plan to Markdown for review (TDD)

**Files:**
- Create: `nutrition/render.py`
- Test: `tests/test_mealplan.py` (append)

- [ ] **Step 1: Write the failing test (append to tests/test_mealplan.py)**

```python
from nutrition.render import render_markdown

def test_render_markdown_lists_all_days(tmp_path):
    mp = load_meal_plan(_sample(tmp_path))
    md = render_markdown(mp)
    assert "# 30-Day Meal Plan" in md
    assert "Day 1" in md and "Day 30" in md
    assert "Rajma with brown rice" in md
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_mealplan.py::test_render_markdown_lists_all_days -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'nutrition.render'`.

- [ ] **Step 3: Write minimal implementation**

```python
# nutrition/render.py
from nutrition.mealplan import MealPlan, MEALS

def render_markdown(mp: MealPlan) -> str:
    lines = ["# 30-Day Meal Plan", ""]
    for d in mp.days:
        lines.append(f"## Day {d['day']}")
        for meal in MEALS:
            lines.append(f"- **{meal.title()}:** {d[meal]['dish']}")
        lines.append("")
    return "\n".join(lines)
```

- [ ] **Step 4: Run test + generate the review file**

Run:
```bash
pytest tests/test_mealplan.py::test_render_markdown_lists_all_days -v
python3 -c "from nutrition.mealplan import load_meal_plan; from nutrition.render import render_markdown; open('data/meal_plan.md','w').write(render_markdown(load_meal_plan('data/meal_plan.json')))"
```
Expected: test PASS; `data/meal_plan.md` created for Anup to read.

- [ ] **Step 5: Commit**

```bash
git add nutrition/render.py tests/test_mealplan.py data/meal_plan.md
git commit -m "feat: render meal plan to markdown"
```

**⛳ CHECKPOINT:** Anup reviews `data/meal_plan.md` before proceeding to Phase 2.

---

## PHASE 2 — YouTube Recipe Matcher

### Task 2.1: YouTube search wrapper (TDD with mocked HTTP)

**Files:**
- Create: `nutrition/youtube.py`
- Test: `tests/test_youtube.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_youtube.py
from unittest.mock import patch, MagicMock
from nutrition.youtube import search_video

def _fake_response():
    m = MagicMock()
    m.json.return_value = {"items": [
        {"id": {"videoId": "abc123"},
         "snippet": {"title": "Best Rajma Recipe", "channelTitle": "Cook With Me"}}
    ]}
    m.raise_for_status.return_value = None
    return m

@patch("nutrition.youtube.requests.get")
def test_search_video_returns_top_hit(mock_get):
    mock_get.return_value = _fake_response()
    result = search_video("Rajma with brown rice", api_key="KEY")
    assert result["videoId"] == "abc123"
    assert result["url"] == "https://www.youtube.com/watch?v=abc123"
    assert "Rajma" in result["title"]

@patch("nutrition.youtube.requests.get")
def test_search_video_none_when_empty(mock_get):
    empty = MagicMock(); empty.json.return_value = {"items": []}
    empty.raise_for_status.return_value = None
    mock_get.return_value = empty
    assert search_video("Nonexistent dish", api_key="KEY") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_youtube.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'nutrition.youtube'`.

- [ ] **Step 3: Write minimal implementation**

```python
# nutrition/youtube.py
import requests

API = "https://www.googleapis.com/youtube/v3/search"

def search_video(dish: str, api_key: str) -> dict | None:
    params = {
        "part": "snippet", "type": "video", "maxResults": 1,
        "q": f"{dish} recipe indian", "relevanceLanguage": "en",
        "videoEmbeddable": "true", "key": api_key,
    }
    r = requests.get(API, params=params, timeout=15)
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        return None
    top = items[0]
    vid = top["id"]["videoId"]
    return {
        "videoId": vid,
        "url": f"https://www.youtube.com/watch?v={vid}",
        "title": top["snippet"]["title"],
        "channel": top["snippet"]["channelTitle"],
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_youtube.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add nutrition/youtube.py tests/test_youtube.py
git commit -m "feat: youtube search wrapper"
```

### Task 2.2: Build `videos.json` cache (TDD)

**Files:**
- Modify: `nutrition/youtube.py` (add `build_video_cache`)
- Test: `tests/test_youtube.py` (append)

- [ ] **Step 1: Write the failing test (append)**

```python
from nutrition.youtube import build_video_cache

def test_build_video_cache_maps_dishes():
    dishes = ["Rajma with brown rice", "Palak paneer with roti"]
    def fake_search(dish, api_key):
        return {"videoId": dish[:3], "url": "u", "title": dish, "channel": "c"}
    cache = build_video_cache(dishes, api_key="KEY", searcher=fake_search)
    assert cache["Rajma with brown rice"]["videoId"] == "Raj"
    assert set(cache.keys()) == set(dishes)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_youtube.py::test_build_video_cache_maps_dishes -v`
Expected: FAIL with `ImportError: cannot import name 'build_video_cache'`.

- [ ] **Step 3: Write minimal implementation (append to nutrition/youtube.py)**

```python
def build_video_cache(dishes: list, api_key: str, searcher=search_video) -> dict:
    cache = {}
    for dish in dishes:
        hit = searcher(dish, api_key)
        if hit:
            cache[dish] = hit
    return cache
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_youtube.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Generate the real cache**

Run (requires real key in `.env`):
```bash
python3 -c "
import os; from dotenv import load_dotenv; load_dotenv()
from nutrition.mealplan import load_meal_plan, all_dishes
from nutrition.youtube import build_video_cache
import json
dishes = all_dishes(load_meal_plan('data/meal_plan.json'))
cache = build_video_cache(dishes, os.environ['YOUTUBE_API_KEY'])
json.dump(cache, open('data/videos.json','w'), indent=2)
print('cached', len(cache), 'videos')
"
```
Expected: prints `cached <N> videos`; `data/videos.json` created.

- [ ] **Step 6: Commit**

```bash
git add nutrition/youtube.py tests/test_youtube.py data/videos.json
git commit -m "feat: build youtube video cache for all dishes"
```

---

## PHASE 3 — WhatsApp Daily Sender

### Task 3.1: `schedule.py` — today's meal selector (TDD)

**Files:**
- Create: `nutrition/schedule.py`
- Test: `tests/test_schedule.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_schedule.py
from datetime import date
from nutrition.schedule import day_index, todays_meals

START = date(2026, 9, 22)  # plan day 1

def test_day_index_wraps_over_30():
    assert day_index(START, START) == 1
    assert day_index(START, date(2026, 10, 21)) == 30      # 29 days later
    assert day_index(START, date(2026, 10, 22)) == 1       # wraps

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_schedule.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'nutrition.schedule'`.

- [ ] **Step 3: Write minimal implementation**

```python
# nutrition/schedule.py
from datetime import date

def day_index(start: date, today: date) -> int:
    delta = (today - start).days
    return (delta % 30) + 1

def todays_meals(meal_plan, start: date, today: date) -> dict:
    idx = day_index(start, today)
    d = meal_plan.days[idx - 1]
    return {"breakfast": d["breakfast"], "lunch": d["lunch"], "dinner": d["dinner"]}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_schedule.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add nutrition/schedule.py tests/test_schedule.py
git commit -m "feat: schedule helpers for daily meal selection"
```

### Task 3.2: `pick_today.py` writes today's payload for Node

**Files:**
- Create: `scripts/pick_today.py`

- [ ] **Step 1: Write the script**

```python
# scripts/pick_today.py
import json, sys
from datetime import date
from nutrition.mealplan import load_meal_plan
from nutrition.schedule import todays_meals

START = date(2026, 9, 22)  # <-- set to your go-live day-1

def main():
    mp = load_meal_plan("data/meal_plan.json")
    videos = json.load(open("data/videos.json"))
    meals = todays_meals(mp, START, date.today())
    payload = {"meals": {}}
    for meal, info in meals.items():
        dish = info["dish"]
        v = videos.get(dish)
        payload["meals"][meal] = {"dish": dish, "video": v}
    json.dump(payload, open("data/today.json", "w"), indent=2)
    print("wrote data/today.json")

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run it**

Run: `python3 scripts/pick_today.py`
Expected: prints `wrote data/today.json`; file lists 3 meals with videos.

- [ ] **Step 3: Commit**

```bash
git add scripts/pick_today.py
git commit -m "feat: pick_today writes daily payload for whatsapp"
```

### Task 3.3: Node message builder (pure fn, TDD)

**Files:**
- Create: `whatsapp/package.json`
- Create: `whatsapp/message.js`
- Test: `whatsapp/test_message.mjs`

- [ ] **Step 1: Create `whatsapp/package.json`**

```json
{
  "name": "whatsapp-sender",
  "version": "0.1.0",
  "type": "module",
  "scripts": { "test": "node test_message.mjs" },
  "dependencies": { "whatsapp-web.js": "^1.23.0", "qrcode-terminal": "^0.12.0" }
}
```

- [ ] **Step 2: Write the failing test**

```javascript
// whatsapp/test_message.mjs
import assert from "node:assert";
import { buildMessage } from "./message.js";

const payload = {
  meals: {
    breakfast: { dish: "Vegetable oats upma", video: { url: "https://youtu.be/abc", title: "Oats Upma" } },
    lunch: { dish: "Rajma", video: { url: "https://youtu.be/def", title: "Rajma" } },
    dinner: { dish: "Palak paneer", video: null }
  }
};
const msg = buildMessage(payload);
assert.ok(msg.includes("Vegetable oats upma"));
assert.ok(msg.includes("https://youtu.be/abc"));
assert.ok(msg.includes("Palak paneer"));
console.log("OK");
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd whatsapp && node test_message.mjs`
Expected: FAIL with `Cannot find module './message.js'`.

- [ ] **Step 4: Write minimal implementation**

```javascript
// whatsapp/message.js
export function buildMessage(payload) {
  const lines = ["🍲 *Today's meals & recipe videos*", ""];
  for (const meal of ["breakfast", "lunch", "dinner"]) {
    const m = payload.meals[meal];
    if (!m) continue;
    const label = meal.charAt(0).toUpperCase() + meal.slice(1);
    lines.push(`*${label}:* ${m.dish}`);
    if (m.video && m.video.url) lines.push(`▶️ ${m.video.url}`);
    lines.push("");
  }
  lines.push("Please prepare as per the videos. Thank you! 🙏");
  return lines.join("\n");
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd whatsapp && node test_message.mjs`
Expected: prints `OK`.

- [ ] **Step 6: Commit**

```bash
git add whatsapp/package.json whatsapp/message.js whatsapp/test_message.mjs
git commit -m "feat: whatsapp message builder + test"
```

### Task 3.4: WhatsApp sender with wa.me fallback

**Files:**
- Create: `whatsapp/send.js`

- [ ] **Step 1: Install deps**

Run: `cd whatsapp && npm install`
Expected: installs `whatsapp-web.js` and `qrcode-terminal`.

- [ ] **Step 2: Write `whatsapp/send.js`**

```javascript
// whatsapp/send.js
import fs from "node:fs";
import pkg from "whatsapp-web.js";
const { Client, LocalAuth } = pkg;
import qrcode from "qrcode-terminal";
import { buildMessage } from "./message.js";

const payload = JSON.parse(fs.readFileSync("../data/today.json", "utf8"));
const text = buildMessage(payload);
const cook = process.env.COOK_WHATSAPP; // e.g. +9198...  (no '+', digits + @c.us)
const chatId = cook.replace(/[^0-9]/g, "") + "@c.us";

function fallback() {
  const link = `https://wa.me/${cook.replace(/[^0-9]/g, "")}?text=${encodeURIComponent(text)}`;
  fs.writeFileSync("../data/whatsapp_fallback.txt", link);
  console.error("Send failed — wrote wa.me fallback link to data/whatsapp_fallback.txt");
}

const client = new Client({ authStrategy: new LocalAuth() });
client.on("qr", (qr) => qrcode.generate(qr, { small: true }));
client.on("ready", async () => {
  try {
    await client.sendMessage(chatId, text);
    console.log("Sent to", chatId);
  } catch (e) {
    fallback();
  } finally {
    await client.destroy();
    process.exit(0);
  }
});
client.on("auth_failure", () => { fallback(); process.exit(1); });
client.initialize();
```

- [ ] **Step 3: First-run login (one-time QR scan)**

Run:
```bash
cd whatsapp && COOK_WHATSAPP="+91YOUROWNNUMBER" node send.js
```
Expected: a QR appears in Terminal; scan with WhatsApp (Linked Devices). Then a **test message arrives on YOUR OWN number**. Auth is cached in `.wwebjs_auth/` for future runs (no QR next time).

- [ ] **Step 4: Commit**

```bash
git add whatsapp/send.js
git commit -m "feat: whatsapp sender with wa.me fallback"
```

---

## PHASE 4 — Grocery Builder + Blinkit Checklist

### Task 4.1: Aggregate a week's ingredients (TDD)

**Files:**
- Create: `nutrition/grocery.py`
- Test: `tests/test_grocery.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_grocery.py
from nutrition.grocery import aggregate_week

def _week_meals():
    # 7 days, each meal one ingredient; oats appears twice
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_grocery.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'nutrition.grocery'`.

- [ ] **Step 3: Write minimal implementation**

```python
# nutrition/grocery.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_grocery.py -v`
Expected: PASS (1 passed).

- [ ] **Step 5: Commit**

```bash
git add nutrition/grocery.py tests/test_grocery.py
git commit -m "feat: weekly ingredient aggregation"
```

### Task 4.2: Blinkit checklist with deep links + supplements (TDD)

**Files:**
- Modify: `nutrition/grocery.py` (add `build_checklist`)
- Test: `tests/test_grocery.py` (append)

- [ ] **Step 1: Write the failing test (append)**

```python
from nutrition.grocery import build_checklist

def test_build_checklist_has_links_and_supplements():
    agg = [{"item": "oats", "count": 7, "quantities": ["50 g"]*7}]
    supplements = [{"name": "Vitamin B12 (methylcobalamin)", "note": "doctor to confirm dose"}]
    md = build_checklist(agg, supplements, week_no=1)
    assert "Week 1" in md
    assert "https://blinkit.com/s/?q=oats" in md
    assert "Vitamin B12" in md
    assert "- [ ]" in md  # tappable checkbox
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_grocery.py::test_build_checklist_has_links_and_supplements -v`
Expected: FAIL with `ImportError: cannot import name 'build_checklist'`.

- [ ] **Step 3: Write minimal implementation (append to nutrition/grocery.py)**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_grocery.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add nutrition/grocery.py tests/test_grocery.py
git commit -m "feat: blinkit checklist with deep links + supplements"
```

### Task 4.3: Weekly build script

**Files:**
- Create: `scripts/build_week.py`

- [ ] **Step 1: Write the script**

```python
# scripts/build_week.py
import json
from datetime import date
from nutrition.mealplan import load_meal_plan
from nutrition.profile import load_profile
from nutrition.schedule import day_index
from nutrition.grocery import aggregate_week, build_checklist

START = date(2026, 9, 22)

def next_week_days(mp, start, today):
    idx = day_index(start, today)  # today's plan-day
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
```

- [ ] **Step 2: Run it**

Run: `python3 scripts/build_week.py`
Expected: prints `wrote data/grocery_week_1.md`; open it to see the tap-to-add checklist.

- [ ] **Step 3: Commit**

```bash
git add scripts/build_week.py
git commit -m "feat: weekly grocery build script"
```

---

## PHASE 5 — Scheduling (macOS launchd)

### Task 5.1: Runner shell scripts

**Files:**
- Create: `scripts/run_daily.sh`
- Create: `scripts/run_weekly.sh`

- [ ] **Step 1: Write `scripts/run_daily.sh`**

```bash
#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
set -a; source .env; set +a
python3 scripts/pick_today.py
cd whatsapp && COOK_WHATSAPP="$COOK_WHATSAPP" node send.js
```

- [ ] **Step 2: Write `scripts/run_weekly.sh`**

```bash
#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
python3 scripts/build_week.py
```

- [ ] **Step 3: Make executable + smoke test**

Run:
```bash
chmod +x scripts/run_daily.sh scripts/run_weekly.sh
./scripts/run_weekly.sh
```
Expected: regenerates the weekly grocery markdown without error.

- [ ] **Step 4: Commit**

```bash
git add scripts/run_daily.sh scripts/run_weekly.sh
git commit -m "feat: daily and weekly runner scripts"
```

### Task 5.2: launchd plists

**Files:**
- Create: `launchd/com.anup.nutrition.daily.plist`
- Create: `launchd/com.anup.nutrition.weekly.plist`

- [ ] **Step 1: Write daily plist (7:30 AM)**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.anup.nutrition.daily</string>
  <key>ProgramArguments</key>
  <array><string>/Users/anup.khandelwal/nutrition-system/scripts/run_daily.sh</string></array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>7</integer><key>Minute</key><integer>30</integer></dict>
  <key>StandardOutPath</key><string>/Users/anup.khandelwal/nutrition-system/data/daily.log</string>
  <key>StandardErrorPath</key><string>/Users/anup.khandelwal/nutrition-system/data/daily.err</string>
</dict></plist>
```

- [ ] **Step 2: Write weekly plist (Sunday 18:00)**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.anup.nutrition.weekly</string>
  <key>ProgramArguments</key>
  <array><string>/Users/anup.khandelwal/nutrition-system/scripts/run_weekly.sh</string></array>
  <key>StartCalendarInterval</key><dict><key>Weekday</key><integer>0</integer><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>/Users/anup.khandelwal/nutrition-system/data/weekly.log</string>
  <key>StandardErrorPath</key><string>/Users/anup.khandelwal/nutrition-system/data/weekly.err</string>
</dict></plist>
```

- [ ] **Step 3: Load the jobs**

Run:
```bash
cp launchd/*.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.anup.nutrition.daily.plist
launchctl load ~/Library/LaunchAgents/com.anup.nutrition.weekly.plist
launchctl list | grep nutrition
```
Expected: both `com.anup.nutrition.daily` and `.weekly` appear.

- [ ] **Step 4: Commit**

```bash
git add launchd/*.plist
git commit -m "feat: launchd schedules for daily send + weekly grocery"
```

**Note (catch-up guard):** `launchd` runs a missed `StartCalendarInterval` job once when the
Mac next wakes, so a sleeping Mac still fires the day's send on wake. No extra code needed.

---

## PHASE 6 — Go Live

### Task 6.1: Switch WhatsApp target to the cook

**Files:**
- Modify: `.env` (local, gitignored)

- [ ] **Step 1: Set the cook's number**

Edit `.env` and set `COOK_WHATSAPP=+91<cook_number>`.

- [ ] **Step 2: Dry run to the cook**

Run: `./scripts/run_daily.sh`
Expected: the cook receives today's 3 meals + video links; `data/daily.log` shows `Sent to ...`.

- [ ] **Step 3: Verify fallback path**

Temporarily set `COOK_WHATSAPP` to an invalid number, run `./scripts/run_daily.sh`, and
confirm `data/whatsapp_fallback.txt` is created with a `wa.me` link. Restore the real number.

### Task 6.2: One-week soak + full test run

- [ ] **Step 1: Run the full suite**

Run: `pytest -v && (cd whatsapp && node test_message.mjs)`
Expected: all Python tests PASS and Node prints `OK`.

- [ ] **Step 2: Observe for one week**

Confirm daily messages arrive at 7:30 AM and the Sunday-evening grocery checklist regenerates.
Tune dishes/videos in `data/*.json` as needed (re-run generators after edits).

- [ ] **Step 3: Final commit**

```bash
git add -A && git commit -m "chore: go-live configuration and soak notes"
```

---

## Self-Review

**Spec coverage:**
- 30-day meal plan → Phase 1 (Tasks 1.1–1.3) ✅
- YouTube matching → Phase 2 (Tasks 2.1–2.2) ✅
- Supplements → in `profile.json` (0.2) + surfaced in grocery checklist (4.2) ✅
- WhatsApp autonomous daily 7:30 → Phase 3 + launchd 5.2 ✅
- wa.me fallback → Task 3.4 ✅
- Weekly Blinkit checklist (B2) → Phase 4 + launchd Sunday ✅
- Mac host / launchd → Phase 5 ✅
- Error handling (send fail, empty video, sleep catch-up, item-not-found) → 3.4, 2.2, 5.2 note, 4.2 ✅

**Placeholder scan:** No TBD/TODO; every code step has full code; every run step has expected output.

**Type consistency:** `load_meal_plan`/`MealPlan.days`, `all_dishes`, `search_video`→dict with `videoId/url/title/channel`, `build_video_cache`, `day_index`/`todays_meals`, `aggregate_week`→rows with `item/count/quantities`, `build_checklist`, `buildMessage` — names consistent across tasks. ✅

**Medical guardrail:** Supplement notes carry "confirm dose with your doctor"; spec disclaimer stands.
