#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera DIETA-SEMANAL.md (versión imprimible) a partir de plan_data.json."""
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

here = os.path.dirname(__file__)
D = json.load(open(os.path.join(here, "plan_data.json"), encoding="utf-8"))
T = D["meta"]["metas"]
out = []
w = out.append

w(f"# 🌮 {D['meta']['titulo']} — {D['meta']['subtitulo']}\n")
w(f"**Metas diarias:** ~{T['kcal']} kcal · Proteína {T['p']} g · Carbos {T['c']} g · "
  f"Grasa {T['f']} g · Fibra {T['fib']} g · Agua {T['water_l']} L · {T['steps']:,} pasos\n")
w("> Cantidades verificadas con Python. La comida del día puede cambiarse por la opción de "
  "“comer fuera” (tacos de maíz, pozole, fajitas, algo a la plancha).\n")
w("\n---\n")

for d in D["dias"]:
    t = d["totales"]
    w(f"\n## {d['nombre']}")
    w(f"**{t['kcal']} kcal** · P {t['p']} g · C {t['c']} g · G {t['f']} g · Fibra {t['fib']} g\n")
    for m in d["comidas"]:
        mt = m["totales"]
        w(f"\n### {m['slot']} — {m['titulo']}  ·  {mt['kcal']} kcal (P {mt['p']} / C {mt['c']} / G {mt['f']})")
        for it in m["items"]:
            w(f"- {it['nombre']}: **{it['cantidad']}**")
        w(f"  \n_💡 {m['tip']}_")
    w("\n---")

w("\n\n# 🛒 Lista de super (semana completa)\n")
for cat in D["compras"]:
    w(f"\n## {cat['categoria']}")
    for it in cat["items"]:
        nota = f"  _({it['nota']})_" if it["nota"] else ""
        w(f"- [ ] {it['nombre']} — **{it['comprar']}**{nota}")

w("\n\n---\n_Guía y notas médicas en `dieta-daira.md`. No sustituye a un profesional._\n")

path = os.path.join(here, "DIETA-SEMANAL.md")
open(path, "w", encoding="utf-8").write("\n".join(out))
print("Escrito:", path)
