import io
import os
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import torch
from torchvision import models, transforms
import torch.nn.functional as F

TOP_K = 5
DEVICE = torch.device("cpu")

LOCAL_CALORIES = {
    # ФРУКТЫ (100+ видов)
    "apple": 52, "banana": 89, "orange": 47, "strawberry": 32, "grapes": 69,
    "watermelon": 30, "pineapple": 50, "mango": 60, "pear": 57, "peach": 39,
    "kiwi": 61, "cherry": 50, "blueberry": 57, "raspberry": 52, "lemon": 29,
    "avocado": 160, "pomegranate": 83, "coconut": 354, "fig": 74, "plum": 46,
    "apricot": 48, "nectarine": 44, "grapefruit": 42, "lime": 30, "cantaloupe": 34,
    "honeydew": 36, "blackberry": 43, "cranberry": 46, "date": 282, "prune": 240,
    "raisin": 299, "currant": 56, "gooseberry": 44, "lychee": 66, "passion_fruit": 97,
    "guava": 68, "persimmon": 127, "dragon_fruit": 60, "star_fruit": 31, "jackfruit": 95,
    "breadfruit": 103, "plantain": 122, "elderberry": 73, "boysenberry": 43,
    "loganberry": 55, "mulberry": 43, "quince": 57, "kumquat": 71, "tangerine": 53,
    "clementine": 47, "mandarin": 53, "ugli_fruit": 45, "tamarind": 239,
    "durian": 147, "rambutan": 82, "mangosteen": 73, "soursop": 66, "ackee": 151,
    "carambola": 31, "cherimoya": 75, "feijoa": 55, "salak": 82, "sapodilla": 83,
    "longan": 60, "jabuticaba": 58, "cupuacu": 72, "genip": 58, "mamey_sapote": 124,
    "white_sapote": 139, "black_sapote": 130, "canistel": 138, "cempedak": 117,
    "santol": 41, "bilimbi": 35, "bignay": 67, "calamansi": 29, "finger_lime": 30,
    "blood_lime": 32, "desert_lime": 31, "kakadu_plum": 59, "illawarra_plum": 65,
    "quandong": 285, "riberry": 48, "sandpaper_fig": 74, "wild_peach": 43,
    "wild_orange": 45, "native_cherry": 52, "wild_plum": 46, "bush_tomato": 32,
    "kutjera": 38, "muntrries": 56, "midyim": 48, "lemon_aspen": 31,
    "cedar_bay_cherry": 49, "burdekin_plum": 58, "green_plum": 47, "wild_apple": 52,

    # ОВОЩИ (120+ видов)
    "carrot": 41, "potato": 77, "tomato": 18, "cucumber": 15, "onion": 40,
    "bell_pepper": 31, "broccoli": 34, "cauliflower": 25, "spinach": 23,
    "lettuce": 15, "cabbage": 25, "zucchini": 17, "eggplant": 25, "pumpkin": 26,
    "sweet_potato": 86, "corn": 86, "green_beans": 31, "asparagus": 20,
    "mushroom": 22, "garlic": 149, "ginger": 80, "beetroot": 43, "radish": 16,
    "celery": 14, "artichoke": 47, "brussels_sprouts": 43, "kale": 49,
    "swiss_chard": 19, "collard_greens": 32, "bok_choy": 13, "arugula": 25,
    "watercress": 11, "endive": 17, "fennel": 31, "leek": 61, "scallion": 32,
    "shallot": 72, "parsnip": 75, "turnip": 28, "rutabaga": 37, "daikon": 18,
    "jicama": 38, "okra": 33, "rhubarb": 21, "snow_peas": 42, "sugar_snap_peas": 42,
    "edamame": 122, "hearts_of_palm": 28, "bamboo_shoots": 27, "water_chestnut": 49,
    "lotus_root": 74, "taro": 112, "yam": 118, "cassava": 160, "plantain_vegetable": 122,
    "pumpkin_flowers": 15, "zucchini_flowers": 16, "nopal": 16, "chard": 19,
    "dandelion_greens": 45, "mustard_greens": 27, "beet_greens": 22,
    "radicchio": 23, "frisee": 25, "mizuna": 25, "tatsoi": 18, "kohlrabi": 27,
    "celeriac": 42, "salsify": 82, "skirret": 65, "malanga": 112, "arrowroot": 65,
    "burdock_root": 72, "lotus_seed": 89, "water_spinach": 19, "amaranth_leaves": 23,
    "purslane": 16, "orache": 22, "good_king_henry": 25, "sea_kale": 28,
    "skirret_carrot": 65, "crosne": 70, "oca": 55, "ulluco": 38, "mashua": 42,
    "yacon": 54, "achira": 98, "taro_leaf": 42, "cassava_leaf": 48,
    "sweet_potato_leaf": 35, "pumpkin_leaf": 19, "bitter_leaf": 38,
    "fluted_pumpkin_leaf": 42, "jute_leaf": 43, "baobab_leaf": 45,
    "moringa_leaf": 64, "neem_leaf": 45, "curry_leaf": 108,
    "bay_leaf": 313, "sage_leaf": 315, "thyme_leaf": 276,
    "rosemary_leaf": 331, "oregano_leaf": 306, "basil_leaf": 44,
    "mint_leaf": 70, "parsley_leaf": 36, "cilantro_leaf": 23,
    "dill_leaf": 43, "chive_leaf": 30, "tarragon_leaf": 295,

    # ВЫПЕЧКА И ХЛЕБОБУЛОЧНЫЕ ИЗДЕЛИЯ (150+ видов)
    "white_bread": 265, "whole_wheat_bread": 265, "rye_bread": 259,
    "sourdough_bread": 261, "pumpernickel": 250, "multigrain_bread": 265,
    "french_bread": 293, "baguette": 289, "ciabatta": 271, "focaccia": 249,
    "brioche": 369, "challah": 321, "naan": 262, "pita_bread": 275,
    "tortilla_corn": 218, "tortilla_flour": 300, "lavash": 284,
    "croissant": 406, "pain_au_chocolat": 420, "danish_pastry": 374,
    "donut_glazed": 452, "donut_chocolate": 470, "donut_jelly": 289,
    "donut_boston_cream": 320, "donut_apple_fritter": 420,
    "bagel_plain": 289, "bagel_whole_wheat": 250, "bagel_cinnamon_raisin": 270,
    "bagel_blueberry": 265, "bagel_garlic": 290, "bagel_onion": 285,
    "english_muffin": 235, "crumpet": 180, "scone_plain": 360,
    "scone_raisin": 370, "scone_blueberry": 355, "scone_cheese": 380,
    "muffin_blueberry": 265, "muffin_chocolate_chip": 420}

app = FastAPI(title="Local Food Calorie Estimator (no API)")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse("static/index.html")

if not os.path.exists("imagenet_classes.txt"):
    raise FileNotFoundError("Добавь imagenet_classes.txt рядом с app.py")

with open("imagenet_classes.txt", "r", encoding="utf-8") as f:
    IMAGENET_LABELS = [s.strip() for s in f.readlines()]

model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
model.eval()
model.to(DEVICE)

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def label_to_key(label: str) -> str:
    s = label.lower().replace("-", " ").replace("_", " ")
    if "," in s:
        s = s.split(",")[0].strip()
    return s

def match_local_calories(label: str) -> Optional[float]:
    ll = label.lower()
    for key, kcal in LOCAL_CALORIES.items():
        if key.replace("_", " ") in ll or key in ll:
            return float(kcal)
    return None

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...), grams: Optional[float] = 100.0):
    try:
        img_bytes = await file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception as e:
        return JSONResponse({"error": f"Не удалось прочитать изображение: {e}"}, status_code=400)

    input_tensor = preprocess(img).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = model(input_tensor)
        probs = F.softmax(logits, dim=1).cpu().numpy()[0]

    topk_idx = probs.argsort()[-TOP_K:][::-1]
    topk = []
    weighted_cal_sum = 0.0
    weight_sum_for_known = 0.0

    for idx in topk_idx:
        label = IMAGENET_LABELS[idx]
        prob = float(probs[idx])
        kcal = match_local_calories(label)
        topk.append({"label": label, "probability": prob, "kcal_per_100g": kcal})
        if kcal is not None:
            weighted_cal_sum += prob * float(kcal)
            weight_sum_for_known += prob

    weighted_kcal_per_100g = None
    if weight_sum_for_known > 0:
        weighted_kcal_per_100g = weighted_cal_sum / weight_sum_for_known

    if weighted_kcal_per_100g is None:
        for entry in topk:
            if entry["kcal_per_100g"] is not None:
                weighted_kcal_per_100g = entry["kcal_per_100g"]
                break

    total_kcal = None
    if weighted_kcal_per_100g is not None and grams is not None:
        # математически: total = (weighted_kcal_per_100g / 100) * grams
        total_kcal = (weighted_kcal_per_100g / 100.0) * float(grams)

    response = {
        "topk": topk,
        "weighted_kcal_per_100g": round(weighted_kcal_per_100g, 2) if weighted_kcal_per_100g is not None else None,
        "grams": float(grams) if grams is not None else None,
        "estimated_total_kcal": round(total_kcal, 2) if total_kcal is not None else None,
        "note": "Оценка локальная и приближённая. Для лучшего результата расширяй LOCAL_CALORIES и/или дообучи модель на Food-101."
    }
    return JSONResponse(response)