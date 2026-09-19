"""One-off author script for the 30-day meal plan (Task 1.2).
Content is curated to Anup's brief: lacto-vegetarian (no eggs), heart-healthy
(low LDL: minimal frying/ghee, soluble fiber via oats/barley/legumes/flax),
B12-conscious (curd/milk/paneer/fortified milk), Vitamin-D-conscious (fortified
milk), North + South Indian mix, no dish repeated within a 5-day window.
Run: python3 scripts/_author_meal_plan.py  -> writes data/meal_plan.json
"""
import json

# 15 of each meal type; cycling 0..14 twice gives a 15-day gap (no 5-day repeat).
BREAKFASTS = [
    ("Vegetable oats upma", [("rolled oats","50 g"),("mixed vegetables","100 g"),("mustard seeds","1 tsp"),("curry leaves","5"),("groundnut oil","1 tsp"),("low-fat curd (side)","100 g")]),
    ("Moong dal chilla with mint chutney", [("yellow moong dal","60 g"),("onion","1"),("green chilli","1"),("coriander","10 g"),("mint chutney","30 g")]),
    ("Idli with sambar", [("idli rice","50 g"),("urad dal","20 g"),("toor dal (sambar)","40 g"),("mixed vegetables","100 g"),("sambar powder","1 tbsp")]),
    ("Besan chilla with low-fat curd", [("besan (gram flour)","60 g"),("tomato","1"),("onion","1"),("spinach","30 g"),("low-fat curd","100 g")]),
    ("Poha with peanuts", [("flattened rice (poha)","60 g"),("peanuts","15 g"),("onion","1"),("peas","30 g"),("groundnut oil","1 tsp"),("lemon","0.5")]),
    ("Ragi dosa with coconut chutney", [("ragi flour","50 g"),("rice flour","20 g"),("coconut chutney","30 g"),("groundnut oil","1 tsp")]),
    ("Vegetable daliya (broken wheat)", [("broken wheat (daliya)","60 g"),("mixed vegetables","100 g"),("fortified toned milk","100 ml"),("cumin","1 tsp")]),
    ("Whole-wheat paneer paratha with curd", [("whole wheat flour","60 g"),("low-fat paneer","50 g"),("groundnut oil","1 tsp"),("low-fat curd","100 g")]),
    ("Sprouts & muesli bowl with fortified milk", [("mixed sprouts","80 g"),("no-sugar muesli","40 g"),("fortified toned milk","200 ml"),("flax seeds","1 tbsp")]),
    ("Rava vegetable upma", [("semolina (rava)","60 g"),("mixed vegetables","100 g"),("curry leaves","5"),("groundnut oil","1 tsp"),("low-fat curd (side)","100 g")]),
    ("Masala oats with sprouts", [("rolled oats","50 g"),("mixed sprouts","50 g"),("tomato","1"),("onion","1"),("turmeric","0.5 tsp")]),
    ("Vegetable uttapam with sambar", [("dosa batter","120 g"),("onion","1"),("tomato","1"),("capsicum","0.5"),("sambar","150 ml")]),
    ("Multigrain veg sandwich with hung curd", [("multigrain bread","2 slices"),("cucumber","0.5"),("tomato","1"),("spinach","20 g"),("hung low-fat curd","60 g")]),
    ("Methi thepla with curd", [("whole wheat flour","60 g"),("fenugreek leaves (methi)","40 g"),("besan","15 g"),("groundnut oil","1 tsp"),("low-fat curd","100 g")]),
    ("Barley vegetable porridge", [("barley","50 g"),("mixed vegetables","80 g"),("fortified toned milk","100 ml"),("almonds","10 g")]),
]

LUNCHES = [
    ("Rajma with brown rice & cucumber raita", [("rajma (kidney beans)","70 g"),("brown rice","60 g"),("onion","1"),("tomato","2"),("low-fat curd","100 g"),("cucumber","1")]),
    ("Chana masala with jowar roti & salad", [("white chana (chickpeas)","70 g"),("jowar flour","60 g"),("onion","1"),("tomato","2"),("mixed salad","100 g")]),
    ("Palak dal with brown rice", [("toor dal","60 g"),("spinach","150 g"),("brown rice","60 g"),("garlic","3 cloves"),("cumin","1 tsp")]),
    ("Mixed veg sabzi, dal & whole-wheat roti", [("whole wheat flour","60 g"),("mixed vegetables","150 g"),("moong dal","50 g"),("groundnut oil","1 tsp")]),
    ("Sambar rice with beans poriyal", [("toor dal","60 g"),("brown rice","60 g"),("french beans","100 g"),("coconut (grated)","15 g"),("sambar powder","1 tbsp")]),
    ("Low-fat kadhi with brown rice", [("besan","40 g"),("low-fat curd","200 g"),("brown rice","60 g"),("fenugreek seeds","0.5 tsp")]),
    ("Lauki chana dal with roti", [("bottle gourd (lauki)","150 g"),("chana dal","60 g"),("whole wheat flour","60 g"),("tomato","1")]),
    ("Brown-rice vegetable pulao with raita", [("brown rice","70 g"),("mixed vegetables","120 g"),("low-fat curd","100 g"),("whole spices","1 tsp"),("cashew","8 g")]),
    ("Masoor dal with roti & bhindi sabzi", [("masoor dal","60 g"),("okra (bhindi)","120 g"),("whole wheat flour","60 g"),("groundnut oil","1 tsp")]),
    ("Curd rice with dal & vegetables", [("brown rice","60 g"),("low-fat curd","150 g"),("moong dal","40 g"),("carrot","1"),("curry leaves","5")]),
    ("Soy chunk curry with roti", [("soy chunks","60 g"),("whole wheat flour","60 g"),("onion","1"),("tomato","2"),("peas","40 g")]),
    ("Toor dal, rice & cabbage poriyal", [("toor dal","60 g"),("brown rice","60 g"),("cabbage","120 g"),("coconut (grated)","10 g"),("mustard seeds","1 tsp")]),
    ("Chole with whole-wheat roti", [("chickpeas","70 g"),("whole wheat flour","60 g"),("onion","1"),("tomato","2"),("chole masala","1 tbsp")]),
    ("Mixed dal with bajra roti & salad", [("mixed dal","60 g"),("bajra flour","60 g"),("mixed salad","100 g"),("cumin","1 tsp")]),
    ("Vegetable bisi bele bath with raita", [("brown rice","60 g"),("toor dal","50 g"),("mixed vegetables","120 g"),("low-fat curd","100 g"),("bisi bele powder","1 tbsp")]),
]

DINNERS = [
    ("Palak paneer with roti", [("spinach","200 g"),("low-fat paneer","70 g"),("whole wheat flour","50 g"),("garlic","3 cloves")]),
    ("Tofu bhurji with roti", [("tofu","100 g"),("onion","1"),("tomato","1"),("capsicum","0.5"),("whole wheat flour","50 g")]),
    ("Mixed vegetable curry, dal & roti", [("mixed vegetables","150 g"),("moong dal","50 g"),("whole wheat flour","50 g"),("groundnut oil","1 tsp")]),
    ("Light paneer tikka masala with roti", [("low-fat paneer","70 g"),("onion","1"),("tomato","2"),("low-fat curd","50 g"),("whole wheat flour","50 g")]),
    ("Vegetable moong khichdi with curd", [("moong dal","50 g"),("brown rice","50 g"),("mixed vegetables","120 g"),("low-fat curd","100 g")]),
    ("Baked lauki kofta with roti", [("bottle gourd","150 g"),("besan","30 g"),("tomato","2"),("whole wheat flour","50 g")]),
    ("Baingan bharta with roti", [("brinjal (baingan)","200 g"),("onion","1"),("tomato","2"),("whole wheat flour","50 g"),("peas","30 g")]),
    ("Light methi matar malai with roti", [("fenugreek leaves","60 g"),("green peas","80 g"),("fortified toned milk","80 ml"),("whole wheat flour","50 g")]),
    ("Paneer bhurji with roti", [("low-fat paneer","80 g"),("onion","1"),("tomato","1"),("capsicum","0.5"),("whole wheat flour","50 g")]),
    ("Vegetable stew with appam", [("mixed vegetables","150 g"),("coconut milk (light)","80 ml"),("appam batter","100 g"),("ginger","1 inch")]),
    ("Dal tadka with roti & salad", [("toor dal","60 g"),("whole wheat flour","50 g"),("mixed salad","100 g"),("garlic","3 cloves"),("cumin","1 tsp")]),
    ("Aloo-gobi with dal & roti", [("cauliflower","150 g"),("potato","1"),("moong dal","50 g"),("whole wheat flour","50 g")]),
    ("Rasam with rice & sauteed veg", [("toor dal","30 g"),("tomato","2"),("brown rice","50 g"),("mixed vegetables","100 g"),("rasam powder","1 tbsp")]),
    ("Tinda sabzi with moong dal & roti", [("tinda (apple gourd)","150 g"),("moong dal","50 g"),("whole wheat flour","50 g"),("tomato","1")]),
    ("Tofu & vegetable stir-fry with roti", [("tofu","100 g"),("broccoli","80 g"),("capsicum","1"),("whole wheat flour","50 g"),("sesame oil","1 tsp")]),
]

def meal(entry):
    dish, ings = entry
    return {"dish": dish, "ingredients": [{"item": i, "qty": q} for i, q in ings]}

days = []
for d in range(30):
    days.append({
        "day": d + 1,
        "breakfast": meal(BREAKFASTS[d % 15]),
        "lunch": meal(LUNCHES[d % 15]),
        "dinner": meal(DINNERS[d % 15]),
    })

with open("data/meal_plan.json", "w") as f:
    json.dump({"days": days}, f, indent=2)
print("wrote data/meal_plan.json with", len(days), "days")
