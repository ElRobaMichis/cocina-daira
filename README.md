# 🌮 La cocina de Daira

App web + plan de alimentación semanal mexicano para Daira, con **macros exactos verificados con Python** y **lista de super con checkboxes**. Funciona **sin conexión**.

---

## 📱 Cómo la usa Daira

**Opción A — abrir el archivo (lo más fácil):**
Abre `index.html` con el navegador (doble clic). Ya funciona, incluso sin internet. Los pendientes que marques en la lista de super se guardan en ese navegador.

**Opción B — instalarla en el celular como app (recomendado):**
1. Sube esta carpeta a un hosting gratis con HTTPS (GitHub Pages, Netlify drop, Vercel…).
2. Abre la URL en el celular (Chrome/Safari).
3. Menú del navegador → **“Agregar a pantalla de inicio”**.
4. Listo: queda como app con ícono, a pantalla completa y **100% offline** (un service worker guarda todo en caché tras la primera carga).

### Qué puede hacer
- **Plan**: ver desayuno / comida / cena / snacks de cada día, con cantidades exactas y macros por comida y por día (barras vs. meta). Incluye un **contador de vasos de agua** (su pendiente #1) y tips por comida.
- **Compras**: lista del super de la semana completa, agrupada por categoría, con **cantidades exactas** y casillas para ir marcando. El progreso y lo marcado se guardan solos.
- **Guía**: sus metas diarias y los recordatorios clave (agua, comer fuera, gastritis, triglicéridos/isotretinoína, antojos, gym).

---

## 🧮 Cómo se calculó (la parte de Python)

`nutrition.py` contiene:
- Una **base de datos de alimentos mexicanos** con macros por 100 g (kcal, proteína, carbos, grasa, fibra).
- El **plan de 7 días** con cantidades exactas en gramos/piezas por ingrediente.
- Verifica que **cada día** caiga en las metas de Daira y lo imprime.
- Agrega la **lista de super** (convirtiendo a peso de compra: factor crudo para carnes, seco para arroz, piezas para tortillas/huevo, latas para atún, etc.).
- Exporta `plan_data.json` (datos legibles) y `plan_data.js` (lo que consume la app).

### Regenerar el plan
Si quieres cambiar una comida o las cantidades:
```bash
python nutrition.py        # reescribe plan_data.json y plan_data.js, y verifica los macros
```
La app toma los cambios al recargar. (Para regenerar íconos: `python make_icons.py`.)

### Resultado de la verificación (actual)
```
Promedio/día  ~1526 kcal | Proteína 114 g (2.15 g/kg) | Carbos 150 g | Grasa 53 g | Fibra 28 g
Todos los días dentro de rango ✔
```

---

## 🗂️ Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | La app (autocontenida: HTML+CSS+JS en un archivo) |
| `plan_data.js` / `plan_data.json` | Los datos del plan (generados por Python) |
| `nutrition.py` | Motor: base de alimentos, plan de 7 días, verificación, lista de super |
| `make_icons.py` / `icons/` | Generador e íconos de la PWA |
| `service-worker.js` | Caché para uso sin conexión |
| `manifest.webmanifest` | Config de la PWA (instalable) |
| `PRODUCT.md` / `DESIGN.md` | Contexto de producto y diseño |
| `dieta-daira.md` | El plan explicado en texto (versión larga, con lo médico) |

---

## ⚕️ Importante

Esto es una guía práctica, **no sustituye a un médico o nutriólogo**. Daira tiene triglicéridos altos (+ isotretinoína), gastritis, colitis y tuvo anemia: conviene que un profesional valide el plan y que se haga análisis (triglicéridos, biometría, perfil tiroideo). El objetivo NO es bajar 8 kg —ya está en peso sano— sino **recomposición y desinflamar** de forma sostenible.
