#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor nutricional del plan de Daira.

- Base de datos de alimentos mexicanos con macros por 100 g (estado "como se come").
- Plan de 7 días (desayuno / comida / cena / snacks) con cantidades EXACTAS en gramos.
- Verifica que cada día caiga dentro de las metas de Daira.
- Agrega la lista de super semanal con cantidades de compra (con factores crudo/seco).
- Exporta plan_data.json y plan_data.js para la app web.

Metas de Daira (mujer, 22, 155 cm, 53 kg, entrena 3x/sem; déficit suave para recomposición):
  ~1500 kcal | Proteína 110-120 g | Grasa 45-55 g | Carbos 140-160 g | Fibra >=25 g
Restricciones: sin cebolla, sin jitomate crudo "solo", sin camarón; pescado solo salmón;
picante moderado (gastritis); bajo en azúcar refinada (triglicéridos + isotretinoína).
"""

import json
import math
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ----------------------------------------------------------------------------
# BASE DE DATOS DE ALIMENTOS  (todo por 100 g "como se come", salvo leche = por 100 ml)
# campos: kcal, p(roteína), c(arbohidrato), f(grasa), fib(ra)   en gramos
# piece_g: gramos por pieza (tortilla, huevo, tostada, bolillo...) si aplica
# cat: categoría de compra
# shop: regla de compra -> ver build_shopping()
# ----------------------------------------------------------------------------
F = {
    # --- Proteínas ---
    "huevo":        dict(nom="Huevo entero",            kcal=143, p=12.6, c=0.7, f=9.5, fib=0,   piece_g=50, cat="Proteína", shop=("pieces", "pza(s)")),
    "clara":        dict(nom="Clara de huevo",          kcal=52,  p=10.9, c=0.7, f=0.2, fib=0,   piece_g=33, cat="Proteína", shop=("egg_white",)),
    "pollo":        dict(nom="Pechuga de pollo",        kcal=165, p=31.0, c=0,   f=3.6, fib=0,   cat="Proteína", shop=("meat", 1.45)),
    "res":          dict(nom="Res magra (bistec)",      kcal=200, p=28.0, c=0,   f=9.0, fib=0,   cat="Proteína", shop=("meat", 1.45)),
    "salmon":       dict(nom="Salmón",                  kcal=206, p=22.0, c=0,   f=13.0,fib=0,   cat="Proteína", shop=("meat", 1.30)),
    "atun":         dict(nom="Atún en agua (escurrido)",kcal=116, p=26.0, c=0,   f=0.8, fib=0,   cat="Proteína", shop=("cans", 100, "lata(s)")),
    "panela":       dict(nom="Queso panela",            kcal=230, p=17.0, c=3.5, f=17.0,fib=0,   cat="Lácteos", shop=("asis",)),
    "requeson":     dict(nom="Requesón",                kcal=138, p=11.0, c=3.0, f=8.0, fib=0,   cat="Lácteos", shop=("asis",)),
    "frijol":       dict(nom="Frijol cocido",           kcal=130, p=8.5,  c=23.0,f=0.5, fib=8.7, cat="Despensa", shop=("asis",)),
    "frijol_ref":   dict(nom="Frijol refrito (poco aceite)", kcal=120, p=7.0, c=18.0, f=2.5, fib=6.0, cat="Despensa", shop=("asis",)),

    # --- Lácteos / bebidas ---
    "leche":        dict(nom="Leche semidescremada",    kcal=47,  p=3.3,  c=4.8, f=1.6, fib=0,   cat="Lácteos", shop=("ml",)),
    "yogur":        dict(nom="Yogur natural sin azúcar",kcal=60,  p=4.0,  c=5.0, f=2.0, fib=0,   cat="Lácteos", shop=("asis",)),
    "crema":        dict(nom="Crema ligera",            kcal=195, p=3.0,  c=5.0, f=18.0,fib=0,   cat="Lácteos", shop=("asis",)),

    # --- Cereales / tortillas ---
    "tortilla":     dict(nom="Tortilla de maíz",        kcal=218, p=5.7,  c=45.0,f=2.7, fib=6.7, piece_g=30, cat="Cereales", shop=("pieces", "pza(s)")),
    "tortilla_h":   dict(nom="Tortilla de harina",      kcal=290, p=8.5,  c=46.0,f=7.0, fib=2.5, piece_g=35, cat="Cereales", shop=("pieces", "pza(s)")),
    "tostada":      dict(nom="Tostada horneada",        kcal=415, p=10.0, c=82.0,f=5.0, fib=11.0,piece_g=12, cat="Cereales", shop=("pieces", "pza(s)")),
    "totopos":      dict(nom="Totopos horneados",       kcal=380, p=8.0,  c=72.0,f=6.0, fib=8.0, cat="Cereales", shop=("asis",)),
    "avena":        dict(nom="Avena (en hojuelas)",     kcal=379, p=13.0, c=67.0,f=6.5, fib=10.0,cat="Cereales", shop=("asis",)),
    "arroz":        dict(nom="Arroz blanco (cocido)",   kcal=130, p=2.7,  c=28.0,f=0.3, fib=0.4, cat="Cereales", shop=("dry", 0.33)),
    "maiz_poz":     dict(nom="Maíz pozolero (cocido)",  kcal=119, p=2.5,  c=24.0,f=1.5, fib=4.0, cat="Despensa", shop=("asis",)),
    "bolillo":      dict(nom="Bolillo",                 kcal=277, p=9.0,  c=54.0,f=2.0, fib=2.3, piece_g=60, cat="Cereales", shop=("pieces", "pza(s)")),

    # --- Grasas / semillas ---
    "aguacate":     dict(nom="Aguacate",                kcal=160, p=2.0,  c=8.5, f=14.7,fib=6.7, cat="Frutas/Verduras", shop=("asis",)),
    "almendra":     dict(nom="Almendras",               kcal=579, p=21.0, c=22.0,f=50.0,fib=12.5,cat="Despensa", shop=("asis",)),
    "nuez":         dict(nom="Nuez",                     kcal=654, p=15.0, c=14.0,f=65.0,fib=6.7, cat="Despensa", shop=("asis",)),
    "chia":         dict(nom="Chía",                     kcal=486, p=17.0, c=42.0,f=31.0,fib=34.0,cat="Despensa", shop=("asis",)),
    "aceite":       dict(nom="Aceite de oliva",          kcal=884, p=0,    c=0,   f=100.0,fib=0,  cat="Despensa", shop=("pantry",)),
    "choco":        dict(nom="Chocolate 70% cacao",     kcal=600, p=7.8,  c=46.0,f=43.0,fib=11.0,cat="Despensa", shop=("asis",)),

    # --- Verduras ---
    "nopal":        dict(nom="Nopal (cocido)",          kcal=15,  p=1.3,  c=3.0, f=0.1, fib=2.0, cat="Frutas/Verduras", shop=("asis",)),
    "champinon":    dict(nom="Champiñón",               kcal=22,  p=3.1,  c=3.3, f=0.3, fib=1.0, cat="Frutas/Verduras", shop=("asis",)),
    "espinaca":     dict(nom="Espinaca",                kcal=23,  p=2.9,  c=3.6, f=0.4, fib=2.2, cat="Frutas/Verduras", shop=("asis",)),
    "calabacita":   dict(nom="Calabacita",              kcal=17,  p=1.2,  c=3.1, f=0.3, fib=1.0, cat="Frutas/Verduras", shop=("asis",)),
    "brocoli":      dict(nom="Brócoli",                 kcal=34,  p=2.8,  c=7.0, f=0.4, fib=2.6, cat="Frutas/Verduras", shop=("asis",)),
    "zanahoria":    dict(nom="Zanahoria",               kcal=41,  p=0.9,  c=10.0,f=0.2, fib=2.8, cat="Frutas/Verduras", shop=("asis",)),
    "pimiento":     dict(nom="Pimiento morrón",         kcal=31,  p=1.0,  c=6.0, f=0.3, fib=2.1, cat="Frutas/Verduras", shop=("asis",)),
    "lechuga":      dict(nom="Lechuga",                 kcal=15,  p=1.4,  c=2.9, f=0.2, fib=1.3, cat="Frutas/Verduras", shop=("asis",)),
    "pepino":       dict(nom="Pepino",                  kcal=15,  p=0.7,  c=3.6, f=0.1, fib=0.5, cat="Frutas/Verduras", shop=("asis",)),
    "chayote":      dict(nom="Chayote",                 kcal=19,  p=0.8,  c=4.5, f=0.1, fib=1.7, cat="Frutas/Verduras", shop=("asis",)),
    "tomate":       dict(nom="Jitomate (para salsa cocida)", kcal=18, p=0.9, c=3.9, f=0.2, fib=1.2, cat="Frutas/Verduras", shop=("asis",)),
    "salsa_v":      dict(nom="Salsa verde",             kcal=30,  p=1.2,  c=5.5, f=0.5, fib=1.5, cat="Despensa", shop=("asis",)),

    # --- Frutas ---
    "platano":      dict(nom="Plátano",                 kcal=89,  p=1.1,  c=23.0,f=0.3, fib=2.6, cat="Frutas/Verduras", shop=("asis",)),
    "manzana":      dict(nom="Manzana",                 kcal=52,  p=0.3,  c=14.0,f=0.2, fib=2.4, cat="Frutas/Verduras", shop=("asis",)),
    "fresa":        dict(nom="Fresa",                   kcal=32,  p=0.7,  c=7.7, f=0.3, fib=2.0, cat="Frutas/Verduras", shop=("asis",)),
    "papaya":       dict(nom="Papaya",                  kcal=43,  p=0.5,  c=11.0,f=0.3, fib=1.7, cat="Frutas/Verduras", shop=("asis",)),
    "guayaba":      dict(nom="Guayaba",                 kcal=68,  p=2.6,  c=14.0,f=0.95,fib=5.0, cat="Frutas/Verduras", shop=("asis",)),
    "mango":        dict(nom="Mango",                   kcal=60,  p=0.8,  c=15.0,f=0.4, fib=1.6, cat="Frutas/Verduras", shop=("asis",)),
    "pera":         dict(nom="Pera",                    kcal=57,  p=0.4,  c=15.0,f=0.1, fib=3.1, cat="Frutas/Verduras", shop=("asis",)),
}

TARGETS = dict(kcal=1500, p=115, f=50, c=150, fib=28, water_l=2.2, steps=8000)
BANDS = dict(kcal=(1420, 1580), p=(108, 124), f=(40, 58), c=(132, 168), fib=(25, 40))

DAY_NAMES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# ----------------------------------------------------------------------------
# EL PLAN  (food_id, gramos, [nota opcional])
# ----------------------------------------------------------------------------
PLAN = [
    # ---------------- LUNES ----------------
    {
        "Desayuno": ("Molletes con café con leche",
                     "Comer algo antes del café (gastritis). Aguacate en vez de cebolla/jitomate.",
                     [("bolillo", 50), ("frijol_ref", 80), ("panela", 40), ("aguacate", 30), ("salsa_v", 20), ("leche", 120)]),
        "Comida":   ("Pozole de pollo",
                     "Carga de lechuga, rábano y orégano; poca tostada frita. Carne magra.",
                     [("maiz_poz", 110), ("pollo", 150), ("lechuga", 50), ("zanahoria", 30), ("tostada", 24)]),
        "Cena":     ("Tostadas de atún",
                     "Atún en agua, aguacate y limón. Liviano para la noche.",
                     [("atun", 100), ("aguacate", 35), ("tostada", 24), ("pepino", 100)]),
        "Snacks":   ("Manzana + almendras, yogur y chocolate",
                     "El chocolate 70% es tu gustito diario, sin culpa.",
                     [("manzana", 110), ("almendra", 15), ("yogur", 150), ("choco", 14)]),
    },
    # ---------------- MARTES ----------------
    {
        "Desayuno": ("Huevos con nopales y salsa verde",
                     "Nopal = fibra que desinflama. Café después del primer bocado.",
                     [("huevo", 50), ("clara", 66), ("nopal", 100), ("tortilla", 60), ("salsa_v", 25), ("leche", 100)]),
        "Comida":   ("Enchiladas verdes de pollo",
                     "Salsa verde NO frita; poca crema y panela en vez de mucho queso.",
                     [("tortilla", 90), ("pollo", 120), ("salsa_v", 40), ("panela", 30), ("crema", 15), ("lechuga", 50), ("nopal", 50)]),
        "Cena":     ("Caldo de pollo con verduras",
                     "Calientito y suave para la gastritis.",
                     [("pollo", 95), ("calabacita", 80), ("zanahoria", 60), ("chayote", 60), ("tortilla", 30)]),
        "Snacks":   ("Manzana + nuez, yogur y chocolate",
                     "La nuez aporta omega-3 (bueno para triglicéridos).",
                     [("manzana", 120), ("nuez", 14), ("yogur", 150), ("choco", 14)]),
    },
    # ---------------- MIÉRCOLES ----------------
    {
        "Desayuno": ("Avena overnight con chía y plátano + huevo",
                     "Se prepara la noche anterior; ideal para días sin tiempo.",
                     [("avena", 40), ("leche", 200), ("chia", 14), ("platano", 80), ("huevo", 100), ("clara", 66)]),
        "Comida":   ("Salmón a la plancha con arroz y verduras",
                     "Salmón (tu pescado favorito) = omega-3. Verduras al vapor.",
                     [("salmon", 110), ("arroz", 75), ("brocoli", 140), ("calabacita", 80)]),
        "Cena":     ("Quesadillas de panela, champiñón y pollo",
                     "Al comal, sin aceite. Salsa al gusto (moderada).",
                     [("tortilla", 60), ("panela", 40), ("champinon", 80), ("pollo", 85), ("salsa_v", 20)]),
        "Snacks":   ("Fresas con yogur y chocolate",
                     "Fresa: dulce natural y mucha agua.",
                     [("fresa", 200), ("yogur", 150), ("choco", 14)]),
    },
    # ---------------- JUEVES ----------------
    {
        "Desayuno": ("Licuado proteico + huevo cocido",
                     "Se lleva en el camino. El huevo cocido sube la proteína.",
                     [("leche", 250), ("avena", 35), ("platano", 60), ("chia", 10), ("huevo", 100)]),
        "Comida":   ("Bistec asado con nopal y frijoles",
                     "Sin cebolla; sazona con ajo, hierbas y poco chile.",
                     [("res", 145), ("nopal", 100), ("frijol", 60), ("tortilla", 60), ("salsa_v", 20)]),
        "Cena":     ("Huevos con espinaca y frijol",
                     "Hierro (espinaca + frijol) con vitamina C del limón.",
                     [("huevo", 50), ("clara", 66), ("espinaca", 80), ("frijol", 50), ("tortilla", 30)]),
        "Snacks":   ("Pera con yogur y chocolate",
                     "La pera es suave y con fibra (pectina): ayuda a la digestión sin irritar.",
                     [("pera", 115), ("yogur", 150), ("choco", 14), ("almendra", 10)]),
    },
    # ---------------- VIERNES ----------------
    {
        "Desayuno": ("Chilaquiles ligeros con pollo",
                     "Totopos horneados (no fritos) y salsa verde.",
                     [("totopos", 30), ("salsa_v", 50), ("huevo", 50), ("clara", 33), ("panela", 25), ("pollo", 45)]),
        "Comida":   ("Tinga de pollo en tostada",
                     "Tinga lleva jitomate COCIDO (no crudo) — sí te funciona.",
                     [("pollo", 115), ("tomate", 60), ("tostada", 36), ("lechuga", 50), ("aguacate", 30), ("frijol", 60)]),
        "Cena":     ("Ensalada de pollo",
                     "Aderezo de limón y aceite de oliva; sin cebolla.",
                     [("pollo", 100), ("lechuga", 60), ("pepino", 80), ("zanahoria", 40), ("aguacate", 30), ("aceite", 3), ("tostada", 12)]),
        "Snacks":   ("Mango con nuez y chocolate",
                     "Mango con chile y limón si quieres tu toque picante.",
                     [("mango", 160), ("nuez", 10), ("choco", 14), ("yogur", 120)]),
    },
    # ---------------- SÁBADO ----------------
    {
        "Desayuno": ("Quesadillas de panela y espinaca + guayaba",
                     "Guayaba: vitamina C que ayuda a absorber el hierro.",
                     [("tortilla", 50), ("panela", 60), ("espinaca", 60), ("salsa_v", 20), ("guayaba", 100)]),
        "Comida":   ("Fajitas de pollo con pimiento",
                     "Pimiento en vez de cebolla. Guacamole en vez de crema.",
                     [("pollo", 160), ("pimiento", 120), ("tortilla_h", 55), ("frijol", 50), ("aguacate", 30)]),
        "Cena":     ("Requesón con verduras y tostada",
                     "Cena ligera y alta en proteína para no picar de noche.",
                     [("requeson", 165), ("pepino", 80), ("zanahoria", 40), ("tostada", 24), ("salsa_v", 15)]),
        "Snacks":   ("Manzana + almendras, yogur y chocolate",
                     "Fin de semana = mantener el rumbo con tu gustito.",
                     [("manzana", 110), ("almendra", 12), ("yogur", 150), ("choco", 14)]),
    },
    # ---------------- DOMINGO ----------------
    {
        "Desayuno": ("Huevos con frijol y aguacate",
                     "Desayuno clásico mexicano, sin jitomate crudo.",
                     [("huevo", 100), ("clara", 66), ("frijol", 80), ("aguacate", 30), ("tortilla", 50), ("salsa_v", 20), ("leche", 100)]),
        "Comida":   ("Caldo de res con verduras",
                     "Reconfortante y nutritivo; carne magra.",
                     [("res", 125), ("zanahoria", 60), ("calabacita", 80), ("chayote", 60), ("arroz", 70), ("tortilla", 30)]),
        "Cena":     ("Sopa de verduras con pollo y panela",
                     "Día de descanso digestivo; cena temprano si puedes.",
                     [("calabacita", 90), ("zanahoria", 40), ("espinaca", 40), ("panela", 45), ("pollo", 60), ("tortilla", 30)]),
        "Snacks":   ("Fresas con nuez, yogur y chocolate",
                     "Cierra la semana con tu gustito.",
                     [("fresa", 160), ("nuez", 8), ("yogur", 150), ("choco", 14)]),
    },
]

# ----------------------------------------------------------------------------
# CÁLCULO
# ----------------------------------------------------------------------------
MACROS = ("kcal", "p", "c", "f", "fib")


def item_macros(fid, grams):
    fo = F[fid]
    k = grams / 100.0
    return {m: fo[m] * k for m in MACROS}


def qty_label(fid, grams):
    fo = F[fid]
    if "piece_g" in fo:
        pieces = grams / fo["piece_g"]
        # redondeo bonito a medias piezas
        pr = round(pieces * 2) / 2
        pr_txt = (str(int(pr)) if pr == int(pr) else str(pr))
        return f"{pr_txt} pza{'s' if pr != 1 else ''} ({int(round(grams))} g)"
    if fid == "leche":
        return f"{int(round(grams))} ml"
    if fid == "atun":
        drained = F["atun"]["shop"][1]
        cans = max(1, int(math.ceil(grams / drained)))
        return f"{cans} lata{'s' if cans != 1 else ''} ({int(round(grams))} g escurrido)"
    return f"{int(round(grams))} g"


def add(into, m):
    for k in MACROS:
        into[k] += m[k]


def round_macros(d):
    return {k: round(v) for k, v in d.items()}


def build():
    days_out = []
    weekly_used = {}  # fid -> gramos totales usados en la semana

    for di, day in enumerate(PLAN):
        day_raw = {m: 0.0 for m in MACROS}      # exacto, para verificar bandas
        day_round = {m: 0 for m in MACROS}       # suma de items redondeados, para mostrar
        meals_out = []
        for slot in ("Desayuno", "Comida", "Cena", "Snacks"):
            title, tip, items = day[slot]
            meal_round = {m: 0 for m in MACROS}
            items_out = []
            for fid, grams in items:
                im = item_macros(fid, grams)
                ir = round_macros(im)
                for m in MACROS:
                    meal_round[m] += ir[m]
                    day_raw[m] += im[m]
                weekly_used[fid] = weekly_used.get(fid, 0) + grams
                items_out.append({
                    "nombre": F[fid]["nom"],
                    "cantidad": qty_label(fid, grams),
                    **ir,
                })
            for m in MACROS:
                day_round[m] += meal_round[m]
            meals_out.append({
                "slot": slot,
                "titulo": title,
                "tip": tip,
                "items": items_out,
                "totales": dict(meal_round),
            })
        days_out.append({
            "idx": di,
            "nombre": DAY_NAMES[di],
            "comidas": meals_out,
            "totales": dict(day_round),
            "_raw_tot": day_raw,
        })

    shopping = build_shopping(weekly_used)
    return days_out, shopping, weekly_used


# ----------------------------------------------------------------------------
# LISTA DE SUPER  (agrega gramos usados -> cantidad a comprar)
# ----------------------------------------------------------------------------
CAT_ORDER = ["Proteína", "Lácteos", "Frutas/Verduras", "Cereales", "Despensa"]
CAT_LABEL = {
    "Proteína": "🍗 Proteínas",
    "Lácteos": "🧀 Lácteos y huevo",
    "Frutas/Verduras": "🥑 Frutas y verduras",
    "Cereales": "🌽 Cereales y tortillas",
    "Despensa": "🫙 Despensa y básicos",
}

# Ingredientes fijos para la salsa verde casera (sustituye a la salsa comprada)
EXTRA_SHOPPING = [
    {"nombre": "Tomate verde (tomatillo)", "comprar": "500 g", "nota": "para la salsa verde casera (ver receta)", "cat": "Frutas/Verduras"},
    {"nombre": "Chile serrano", "comprar": "2 pzas", "nota": "para la salsa verde (sin semillas)", "cat": "Frutas/Verduras"},
    {"nombre": "Ajo", "comprar": "1 cabeza", "nota": "para la salsa verde (1 diente asado)", "cat": "Frutas/Verduras"},
    {"nombre": "Cilantro", "comprar": "1 manojo", "nota": "para la salsa verde", "cat": "Frutas/Verduras"},
]


def roundup(x, step):
    return int(math.ceil(x / step) * step)


def build_shopping(weekly_used):
    cats = {c: [] for c in CAT_ORDER}
    for fid, grams in weekly_used.items():
        if fid == "salsa_v":
            continue  # se hace casera (ver receta); sus ingredientes van en EXTRA_SHOPPING
        fo = F[fid]
        rule = fo["shop"]
        kind = rule[0]
        note = ""
        if kind == "meat":
            raw = grams * rule[1]
            buy = roundup(raw, 50)
            label = f"{buy} g" if buy < 1000 else f"{buy/1000:.2f} kg".replace(".00", "")
            note = "peso crudo aprox."
        elif kind == "cans":
            drained = rule[1]
            cans = max(1, int(math.ceil(grams / drained)))
            label = f"{cans} {rule[2]}"
            note = "atún en agua"
        elif kind == "pieces":
            pieces = grams / fo["piece_g"]
            buy = int(math.ceil(pieces))
            label = f"{buy} {rule[1]}"
        elif kind == "egg_white":
            eggs = int(math.ceil(grams / 33.0))
            label = f"{eggs} pza(s)"
            note = "para las claras: claras de cartón, o esos huevos aparte de los enteros"
        elif kind == "dry":  # cocido -> seco
            dry = grams * rule[1]
            buy = roundup(dry, 25)
            label = f"{buy} g"
            note = "peso en crudo/seco"
        elif kind == "ml":
            buy = roundup(grams, 100)
            label = f"{buy} ml" if buy < 1000 else f"{buy/1000:.1f} L".replace(".0", "")
        elif kind == "pantry":
            label = "al gusto"
            note = "ya en despensa"
        else:  # asis
            buy = roundup(grams * 1.06, 10)  # +6% merma/buffer
            label = f"{buy} g" if buy < 1000 else f"{buy/1000:.2f} kg".replace(".00", "")

        cats[fo["cat"]].append({
            "id": fid,
            "nombre": fo["nom"],
            "comprar": label,
            "nota": note,
            "_g": round(grams),
        })

    for ex in EXTRA_SHOPPING:
        cats[ex["cat"]].append({"id": ex["nombre"], "nombre": ex["nombre"],
                                "comprar": ex["comprar"], "nota": ex["nota"], "_g": 0})

    out = []
    for c in CAT_ORDER:
        items = sorted(cats[c], key=lambda x: x["nombre"])
        if items:
            out.append({"categoria": CAT_LABEL[c], "items": items})
    return out


# ----------------------------------------------------------------------------
# REPORTE / VERIFICACIÓN
# ----------------------------------------------------------------------------
def verify_and_report(days):
    print("=" * 72)
    print("VERIFICACIÓN DEL PLAN  (metas: ~1500 kcal | P 110-120 | G 45-55 | C 140-160 | Fib >=25)")
    print("=" * 72)
    ok_all = True
    wk = {m: 0.0 for m in MACROS}
    for d in days:
        t = d["_raw_tot"]
        for m in MACROS:
            wk[m] += t[m]
        flags = []
        for m in ("kcal", "p", "f", "c", "fib"):
            lo, hi = BANDS[m]
            if not (lo <= t[m] <= hi):
                flags.append(f"{m}={t[m]:.0f}!(fuera {lo}-{hi})")
        status = "OK " if not flags else "REV"
        if flags:
            ok_all = False
        print(f"{status} {d['nombre']:<10} "
              f"kcal {t['kcal']:>5.0f} | P {t['p']:>5.1f} | C {t['c']:>5.1f} | "
              f"G {t['f']:>5.1f} | Fib {t['fib']:>4.1f}"
              + ("   <-- " + ", ".join(flags) if flags else ""))
    print("-" * 72)
    n = len(days)
    print(f"PROMEDIO/día  kcal {wk['kcal']/n:>5.0f} | P {wk['p']/n:>5.1f} | "
          f"C {wk['c']/n:>5.1f} | G {wk['f']/n:>5.1f} | Fib {wk['fib']/n:>4.1f}")
    print(f"Proteína: {wk['p']/n/53:.2f} g/kg  |  kcal de proteína: {100*wk['p']*4/wk['kcal']:.0f}%")
    print("RESULTADO:", "TODOS LOS DÍAS EN RANGO ✔" if ok_all else "HAY DÍAS A AJUSTAR ✗")
    print("=" * 72)
    return ok_all


def main():
    days, shopping, weekly = build()
    ok = verify_and_report(days)

    # limpiar campo interno antes de exportar
    for d in days:
        d.pop("_raw_tot", None)

    data = {
        "meta": {
            "titulo": "Plan de Daira",
            "subtitulo": "7 días · cocina mexicana nutritiva",
            "metas": TARGETS,
            "nota": "Cantidades verificadas con Python. Macros aproximados (±5%). "
                    "La comida del día puede cambiarse por la opción de 'comer fuera' de la guía.",
        },
        "dias": days,
        "compras": shopping,
        "guia": GUIA,
        "recetas": RECETAS,
    }
    out_json = os.path.join(os.path.dirname(__file__), "plan_data.json")
    out_js = os.path.join(os.path.dirname(__file__), "plan_data.js")
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    with open(out_js, "w", encoding="utf-8") as fh:
        fh.write("window.PLAN_DATA = ")
        json.dump(data, fh, ensure_ascii=False)
        fh.write(";\n")
    print(f"Escrito: {out_json}")
    print(f"Escrito: {out_js}")
    return ok


# Recetas base que se muestran en la app (se llenan tras la investigación)
# cada receta: nombre, rendimiento, conservacion, usa, ingredientes[{nombre,cantidad}], pasos[], nota
RECETAS = [
    {
        "nombre": "Salsa verde asada (sin cebolla)",
        "rendimiento": "~340 g (1 lote)",
        "conservacion": "3-4 días en refri; haz 2 lotes chicos o congela la mitad",
        "usa": "los 7 días (~230 g a la semana)",
        "ingredientes": [
            {"nombre": "Tomate verde (tomatillo), sin cáscara y lavado", "cantidad": "400 g"},
            {"nombre": "Chile serrano (asado, SIN semillas ni venas)", "cantidad": "1 pza (~12 g)"},
            {"nombre": "Ajo (asado y luego pelado)", "cantidad": "1 diente (~5 g)"},
            {"nombre": "Cilantro fresco (hojas y tallos tiernos)", "cantidad": "20 g (1/3 taza)"},
            {"nombre": "Sal", "cantidad": "4 g (3/4 cdita)"},
            {"nombre": "Azúcar (para cortar la acidez)", "cantidad": "1 pizca"},
            {"nombre": "Agua (para ajustar al licuar)", "cantidad": "30-50 ml"},
        ],
        "pasos": [
            "Calienta un comal a fuego medio y pon los tomatillos, el chile serrano y el ajo sin pelar.",
            "Tatema 8-10 min volteando, hasta que la piel de los tomatillos tenga manchas negras y estén suaves. Saca el ajo y el chile antes si se queman.",
            "Deja enfriar un poco. Pela el ajo. Al chile córtale el rabo y ábrelo para quitar TODAS las semillas y venas (eso baja el picor para tu gastritis).",
            "Licúa los tomatillos con sus jugos junto con el ajo, el chile (solo la pulpa), el cilantro, la sal y la pizca de azúcar. Agrega agua poco a poco solo si la quieres más fluida.",
            "Prueba y ajusta de sal. Para una versión aún más suave, licúa 1/4 de aguacate (te gusta y baja la acidez).",
            "Pásala a un frasco limpio con tapa y refrigérala.",
        ],
        "nota": "Adaptada para gastritis: tomatillo TATEMADO (no crudo), 1 solo chile SIN semillas, ajo ASADO y SIN cebolla. No la uses en ayunas, siempre con comida. Fuentes: Pati Jinich y Directo al Paladar México.",
    },
]

# Consejos / guía que también se muestran en la app
GUIA = [
    {"t": "💧 Agua", "d": "Meta 2–2.5 L al día (hoy tomas ~500 ml). Llena una botella de 1 L dos veces. Esto es lo que más te va a desinflamar."},
    {"t": "🍽️ Comer fuera", "d": "Cuando comas con tu novio: tacos de maíz, pozole, fajitas, enchiladas verdes o algo a la plancha. Evita lo frito y el refresco. Cambia la comida del día por esto sin problema."},
    {"t": "🔥 Gastritis", "d": "No te saltes comidas, café nunca en ayunas, picante moderado y baja el refresco (incluida Coca Zero)."},
    {"t": "🩸 Triglicéridos + isotretinoína", "d": "Menos azúcar y harinas blancas, cero alcohol, más omega-3 (salmón, nuez, chía). Que tu derma te monitoree triglicéridos e hígado."},
    {"t": "🍫 Antojos", "d": "El chocolate 70% diario ya está en el plan. El postre de las citas es tu comida libre de la semana: disfrútalo sin culpa."},
    {"t": "🏋️ Gym", "d": "Prioriza pesas/fuerza sobre cardio para marcar. En días de gym puedes comer ~100-150 kcal más (fruta o tortilla extra)."},
    {"t": "😴 Sueño y pasos", "d": "Intenta dormir más (hoy ~5 h): sube cortisol y antojos. Sube de 3,700 a ~8,000 pasos caminando entre clases."},
    {"t": "📋 Pendiente médico", "d": "Hazte análisis: triglicéridos, biometría (anemia) y perfil tiroideo. Idealmente valida este plan con un nutriólogo."},
]


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
