# Automated Personalized Nutrition System

An autonomous system that turns blood-test findings into a personalized meal plan, sends daily recipe videos to your cook via WhatsApp, and generates weekly grocery checklists — all running on macOS with zero manual intervention.

## What It Does

```
Blood Report → 30-Day Meal Plan → YouTube Recipe Videos → Daily WhatsApp → Weekly Grocery List
```

**Daily (7:30 AM):**
- Picks today's 3 meals from your personalized 30-day plan
- Fetches matching YouTube recipe video links
- Sends a WhatsApp message to your cook with dishes + videos

**Weekly (Sunday 6 PM):**
- Aggregates the coming week's ingredients
- Generates a Blinkit grocery checklist with tap-to-add deep links
- Includes supplement recommendations

## Example Output

**Daily WhatsApp message to cook:**
```
🍲 *Today's meals & recipe videos*

*Breakfast:* Vegetable oats upma
▶️ https://www.youtube.com/watch?v=...

*Lunch:* Rajma with brown rice & cucumber raita
▶️ https://www.youtube.com/watch?v=...

*Dinner:* Palak paneer with roti
▶️ https://www.youtube.com/watch?v=...

Please prepare as per the videos. Thank you! 🙏
```

**Weekly Blinkit grocery checklist:**
```markdown
# Blinkit Grocery Checklist — Week 1

## Groceries
- [ ] oats (x7) — [add](https://blinkit.com/s/?q=oats)
- [ ] brown rice (x5) — [add](https://blinkit.com/s/?q=brown+rice)
- [ ] spinach (x3) — [add](https://blinkit.com/s/?q=spinach)
...

## Supplements (confirm dose with your doctor)
- [ ] Vitamin B12 (methylcobalamin) — [add](https://blinkit.com/s/?q=...)
- [ ] Vitamin D3 — [add](https://blinkit.com/s/?q=...)
```

## Architecture

```
nutrition-system/
├── nutrition/          # Python package (meal plan, YouTube, grocery logic)
├── scripts/            # Daily/weekly runners + meal plan authoring
├── whatsapp/           # Node.js WhatsApp sender (whatsapp-web.js)
├── launchd/            # macOS scheduling (cron-like)
├── data/               # Your profile, meal plan, video cache (gitignored except examples)
├── tests/              # 13 pytest tests + 1 Node test
└── docs/               # Design spec + implementation plan
```

**Tech stack:** Python 3.11+, Node 18+, YouTube Data API v3, WhatsApp Web (via `whatsapp-web.js`), macOS `launchd`.

## Requirements

- **macOS** (tested on macOS 14+; launchd scheduling)
- **Python 3.11+** (with `pip`)
- **Node.js 18+** (with `npm`)
- **YouTube Data API key** (free; see Setup)
- **WhatsApp account** (for sending; requires one-time QR scan)

## Setup

### 1. Clone and Install Dependencies

```bash
git clone https://github.com/anup4khandelwal/nutrition-system.git
cd nutrition-system

# Python
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Node (WhatsApp sender)
cd whatsapp && npm install && cd ..
```

### 2. Get a YouTube Data API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → **APIs & Services → Library** → enable **YouTube Data API v3**
3. **Credentials → Create credentials → API key**
4. Copy the key

### 3. Configure Your Profile

Edit `data/profile.json` (or create from your blood report):
```json
{
  "person": { "name": "Your Name", "age": 42, "sex": "male" },
  "diet": { "type": "lacto-vegetarian", "eggs": false, ... },
  "flags": { "vitamin_b12_deficient": true, ... },
  "targets": { "calories_kcal": 2200, "fiber_g": 35, ... },
  "emphasize_foods": ["oats", "legumes", ...],
  "supplements": [...]
}
```

### 4. Create Your Meal Plan

Run the authoring script or manually write `data/meal_plan.json`:
```bash
python3 scripts/_author_meal_plan.py
```
Validate: `python3 -c "from nutrition.mealplan import load_meal_plan; load_meal_plan('data/meal_plan.json')"`

### 5. Build the YouTube Video Cache

Create `.env`:
```bash
YOUTUBE_API_KEY=your_key_here
COOK_WHATSAPP=+91XXXXXXXXXX
```

Generate video cache:
```bash
source .venv/bin/activate
python3 -c "
from nutrition.mealplan import load_meal_plan, all_dishes
from nutrition.youtube import build_video_cache
import json, os
from dotenv import load_dotenv; load_dotenv()
dishes = all_dishes(load_meal_plan('data/meal_plan.json'))
cache = build_video_cache(dishes, os.environ['YOUTUBE_API_KEY'])
json.dump(cache, open('data/videos.json','w'), indent=2)
"
```

### 6. WhatsApp Login (One-Time QR Scan)

```bash
cd ~/nutrition-system && set -a && source .env && set +a && cd whatsapp && node send.js
```
Scan the QR code with **WhatsApp → Linked Devices** on your phone. The session is cached in `.wwebjs_auth/` (gitignored).

### 7. Test the Daily Send

```bash
./scripts/run_daily.sh
```
Check `data/daily.log` for success. Your cook should receive a message.

### 8. Activate Scheduling

```bash
cp launchd/*.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.anup.nutrition.daily.plist
launchctl load ~/Library/LaunchAgents/com.anup.nutrition.weekly.plist
launchctl list | grep nutrition
```

Done. The system now runs autonomously.

## Testing

```bash
# Python tests (13 tests)
pytest -v

# Node test
cd whatsapp && node test_message.mjs
```

## Customization

### Change the Schedule

Edit `launchd/*.plist`:
- **Daily time:** `<key>Hour</key><integer>7</integer>` (7:30 AM)
- **Weekly day:** `<key>Weekday</key><integer>0</integer>` (Sunday = 0)

Reload: `launchctl unload ... && launchctl load ...`

### Swap Dishes in the Meal Plan

Edit `data/meal_plan.json` or re-run `scripts/_author_meal_plan.py`, then regenerate videos:
```bash
python3 scripts/regenerate_videos.py  # (or re-run the cache build snippet above)
```

### Use a Different Grocery Platform

Modify `nutrition/grocery.py` → `_blinkit_link()` to generate deep links for your platform (e.g., BigBasket, Amazon Fresh).

## File Structure

| Path | What | Tracked in Git? |
|------|------|----------------|
| `data/profile.json` | Your health profile + diet prefs | ✅ Yes (force-added) |
| `data/meal_plan.json` | 30-day meal plan | ✅ Yes |
| `data/videos.json` | YouTube video cache (dish → videoId) | ✅ Yes |
| `.env` | API key + phone number (secrets) | ❌ No (gitignored) |
| `data/today.json` | Daily payload (runtime) | ❌ No |
| `data/*.log`, `*.err` | Runtime logs | ❌ No |
| `.wwebjs_auth/` | WhatsApp session cache | ❌ No |

## Design & Planning

Full design documentation:
- **Spec:** [`docs/superpowers/specs/2026-09-19-nutrition-system-design.md`](docs/superpowers/specs/2026-09-19-nutrition-system-design.md)
- **Implementation Plan:** [`docs/superpowers/plans/2026-09-19-nutrition-system.md`](docs/superpowers/plans/2026-09-19-nutrition-system.md)

## Medical Disclaimer

⚠️ **This system is not medical advice.** It reads blood-report data and suggests meals/supplements based on your configuration. Always consult a qualified physician before:
- Starting any supplement regimen
- Making significant dietary changes
- Interpreting blood test results

The author is not liable for health outcomes.

## Troubleshooting

**WhatsApp send fails:**
- Check `data/whatsapp_fallback.txt` for a `wa.me` one-tap link
- Re-run QR login if session expired: `cd whatsapp && node send.js`

**YouTube quota exceeded:**
- Free tier = 10,000 units/day; building a 45-video cache uses ~4,500
- Wait 24h or apply for a quota increase

**Mac asleep at 7:30 AM:**
- macOS launchd runs the job when the Mac next wakes (catch-up behavior)

**Grocery list shows "week_4" before start date:**
- The week numbering is cosmetic only; grocery contents are always correct for the next 7 days

## Credits

Built with:
- [whatsapp-web.js](https://github.com/pedroslopez/whatsapp-web.js)
- YouTube Data API v3
- Python (pytest, requests, python-dotenv)
- Node.js

Developed as a personal nutrition automation system. Open-sourced for reference.

## License

MIT License. See `LICENSE` file (if added). Use at your own risk.
