# Automated Personalized Nutrition System — Design Spec

**Date:** 2026-09-19
**Owner:** Anup Khandelwal
**Status:** Approved (design), pending implementation plan

> ⚠️ **Medical disclaimer:** This system reads blood-report data and generates diet/supplement
> suggestions. It is not medical advice. All supplement dosing (especially Vitamin B12 and
> Vitamin D3) and the past elevated TSH must be confirmed with a qualified physician before use.

---

## 1. Purpose

Build a mostly-autonomous system on Anup's Mac that:
1. Turns his blood-report findings into daily nutrient targets + a supplement stack.
2. Generates a 30-day Indian vegetarian (lacto, no eggs) meal plan meeting those targets.
3. Matches each dish to a tasty, cook-friendly YouTube recipe video.
4. Sends the day's recipe video to his cook via WhatsApp automatically each morning.
5. Produces a weekly Blinkit grocery checklist (with deep links + supplements) that Anup taps to add and pays for himself.

## 2. Input: Blood Report Findings (14 Aug 2026, Tata 1mg)

Clinically significant / actionable flags:

| Marker | Value | Ref range | Status | Implication |
|---|---|---|---|---|
| Vitamin B12 | < 148 pg/mL | 187–833 | Deficient (was 424 on 09 Jul) | Supplement needed; diet alone insufficient for vegetarian |
| Vitamin D (25-OH) | 14.1 ng/mL | 30–100 | Deficient (was 37.9) | Supplement + sunlight + fortified foods |
| LDL Cholesterol | 127 mg/dL | ≤ 99.9 | High | Low-saturated-fat, high-soluble-fiber diet |
| Non-HDL Cholesterol | 153 mg/dL | ≤ 129.9 | High | Same as LDL |
| HDL | 41 mg/dL | ≥ 39.5 | Low-ish | Healthy fats + exercise |
| Total Cholesterol | 193 mg/dL | ≤ 199.9 | Borderline | Monitor |
| HbA1c / Fasting glucose | 5.2% / 90 | Normal | Good | Maintain |
| TSH | 1.42 | 0.35–4.94 | Normal now (was 6.76 on 09 Jul) | Flag to doctor |
| Liver, Kidney, Iron, Hb | — | — | Normal | — |

**Meal-plan brief derived:** Indian vegetarian (lacto, no eggs), North + South Indian mix,
heart-healthy (lower LDL/Non-HDL), high soluble fiber, B12- and Vitamin-D-conscious,
3 meals/day, cook is fairly skilled, no dislikes/allergies.

## 3. Locked Decisions

| Area | Decision |
|---|---|
| Grocery platform | Blinkit |
| Grocery approach | B2 — smart checklist + deep links; Anup signs in & pays himself |
| WhatsApp delivery | W3 — WhatsApp Web automation (`whatsapp-web.js`) + `wa.me` fallback |
| Send mode | Fully autonomous, daily at 7:30 AM |
| Grocery list cadence | Generated Sunday evening |
| Host | Anup's Mac first (migrate to Pi/VM later if desired) |
| YouTube sourcing | Official YouTube Data API |
| Builder | Goose, end-to-end |

## 4. Architecture

Single local Python project. Four independent modules + a `profile.json` data source,
driven by two scheduled jobs (macOS `launchd`).

```
data/profile.json (nutrient targets + prefs, built once)
        │
        ├──▶ 1. Meal Plan Engine ──▶ meal_plan.json (30d × 3 meals)
        │                                   │
        │                                   ├──▶ 2. Recipe/YouTube Matcher ──▶ videos.json
        │                                   │           │
        │                                   │           └──▶ 4a. WhatsApp Sender (daily 7:30 AM)
        │                                   │
        │                                   └──▶ 3. Grocery Builder ──▶ grocery_week_N.json
        │                                               │
        │                                               └──▶ 4b. Blinkit Checklist (Sun eve)
        │
        └── Scheduler: launchd fires 4a daily; (3+4b) Sunday evening
```

## 5. Modules

### Module 1 — Meal Plan Engine
- **Input:** `profile.json`.
- **Output:** `meal_plan.json` — 30 days × {breakfast, lunch, dinner}; each meal has
  dish name, key nutrients, ingredient list w/ quantities.
- **How:** LLM-generated once, reviewed against targets. Deterministic thereafter (no daily LLM call).

### Module 2 — Recipe/YouTube Matcher
- **Input:** dish names from `meal_plan.json`.
- **Process:** YouTube Data API search per dish; filter by views, language (Hindi/English),
  reputable channels; pick best `videoId`.
- **Output:** `videos.json` (dish → videoId + title + url), cached for stability.

### Module 3 — Grocery Builder
- **Input:** next 7 days of meals + supplement stack.
- **Process:** aggregate & consolidate ingredient quantities; categorize.
- **Output:** `grocery_week_N.json`.

### Module 4a — WhatsApp Sender (daily 7:30 AM)
- Reads today's dish + video; formats message; sends via `whatsapp-web.js` (one-time QR login).
- **Fallback:** on failure, write a `wa.me` deep-link file for one-tap manual send.

### Module 4b — Blinkit Checklist (Sunday evening)
- Converts `grocery_week_N.json` into a checklist with Blinkit deep-links
  (`blinkit.com/s/?q=<item>`). Anup taps-add each item, signs in, pays.

## 6. Data Flow

- **One-time setup:** report → `profile.json` → Module 1 → `meal_plan.json` → Module 2 → `videos.json`. Reviewed by Anup once.
- **Daily 7:30 AM:** scheduler → Module 4a → cook receives video.
- **Weekly Sun eve:** scheduler → Module 3 → `grocery_week_N.json` → Module 4b → Anup gets link list → pays.

## 7. Supplement Stack (confirm with physician)

| Supplement | Rationale | Typical form (doctor to finalize) |
|---|---|---|
| Vitamin B12 | Deficient (<148); veg diet insufficient | Methylcobalamin 1500 mcg/day (possible short high-dose course) |
| Vitamin D3 | Deficient (14.1) | 60,000 IU weekly × 8 wks then maintenance |
| Omega-3 (algal, veg) | High LDL/Non-HDL, low HDL | 500–1000 mg EPA+DHA/day |
| Soluble fiber (dietary, not pill) | Lower LDL | oats, barley, flax, legumes — built into plan |

Supplements are auto-added to the weekly Blinkit list.

## 8. Error Handling

- **WhatsApp send failure** → write `wa.me` fallback link + log; no silent failure.
- **YouTube API quota/empty result** → keep last cached video for that dish; log for review.
- **Scheduler miss (Mac asleep)** → on next wake, run any missed daily job once (catch-up guard).
- **Grocery item not found on Blinkit** → still listed in checklist with a plain search link.

## 9. Build Phases

| Phase | Deliverable | Anup sees |
|---|---|---|
| 0. Setup | Python project + `profile.json` from report | Repo on Mac |
| 1. Meal plan | Module 1 → 30-day plan (JSON + readable MD/PDF) | 30-day plan to review |
| 2. Videos | YouTube API key + Module 2 → `videos.json` | Each dish paired w/ video |
| 3. WhatsApp | Module 4a + `whatsapp-web.js`; test to Anup's own number | Test message received |
| 4. Grocery | Modules 3 + 4b → first week checklist | Tap-to-add shopping list |
| 5. Schedule | `launchd` jobs (daily 7:30, Sunday eve) | Runs on its own |
| 6. Go live | Switch WhatsApp target to cook; run a week; tune | Fully autonomous |

## 10. Inputs Required From Anup

- YouTube Data API key (Phase 2)
- One-time WhatsApp Web QR scan (Phase 3)
- Cook's WhatsApp number (Phase 6)
- Blinkit login — only Anup, only at payment time

## 11. Out of Scope (YAGNI)

- True Blinkit auto-cart/auto-pay (chosen B2 instead).
- WhatsApp Cloud API / Meta Business setup.
- Cloud/Pi hosting (Mac-first; revisit later).
- Human-in-the-loop approval of daily videos (chosen fully autonomous).
