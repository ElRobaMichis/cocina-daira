# Design

Mood: *cocina mexicana de mañana — luz cálida sobre cal y talavera, comal y limón fresco.* Warm and homey, but the surfaces stay clean and bright so the food feels nutritious, not heavy.

## Color (OKLCH)

Strategy: **Committed-but-restrained** — clean near-white surfaces; a warm terracotta primary carries the Mexican identity; a fresh green signals "nutritivo" and drives progress/checks. (Deliberate warm override of the cobalt seed: the brief is culturally environmental.)

| Role | OKLCH | Use |
|---|---|---|
| `--bg` | `oklch(0.994 0.004 70)` | App background, barely-warm off-white (near pure) |
| `--surface` | `oklch(1 0 0)` | Cards, sheets (pure white, lifts off bg) |
| `--surface-2` | `oklch(0.975 0.008 70)` | Insets, headers, list rows |
| `--ink` | `oklch(0.24 0.02 45)` | Primary text (~13:1 on bg) |
| `--ink-soft` | `oklch(0.44 0.02 45)` | Secondary text (~5.6:1, AA) |
| `--line` | `oklch(0.90 0.01 60)` | Borders, dividers |
| `--primary` | `oklch(0.56 0.16 38)` | Terracotta/chili — brand, headers, primary action |
| `--primary-press` | `oklch(0.50 0.16 38)` | Pressed/active |
| `--primary-tint` | `oklch(0.95 0.03 45)` | Primary wash (selected day, chips) |
| `--green` | `oklch(0.62 0.14 150)` | Nutritivo accent: checks, protein, success |
| `--green-tint` | `oklch(0.95 0.04 150)` | Checked rows, progress track fill bg |
| `--amber` | `oklch(0.78 0.13 75)` | Carbs macro |
| `--gold` | `oklch(0.72 0.10 95)` | Fat macro |
| `--leaf` | `oklch(0.70 0.10 140)` | Fiber macro |

Macro color map: **Proteína = green**, **Carbos = amber**, **Grasa = gold**, **Fibra = leaf**. Consistent everywhere.

## Typography

- **Display/headings:** `Fraunces` (warm characterful serif) for app title, day name, meal titles — appetizing, editorial warmth. Fallback `Georgia, 'Times New Roman', serif`.
- **UI/body/data:** `Inter` for everything else; fallback `system-ui, -apple-system, Segoe UI, Roboto, sans-serif`.
- Loaded via Google Fonts with `display=swap`; **fallbacks are first-class** so offline first-load still looks right. Service worker caches them after first online load.
- Product scale: fixed rem (not fluid). Base 16px; steps ~1.2. Numbers/macros use `font-variant-numeric: tabular-nums`.

## Motion

150–250ms, ease-out. State-conveying only: day switch crossfade, sheet expand, checkbox check (with a subtle green fill + strike), progress bars grow on view. Full `prefers-reduced-motion` fallback (instant). Staggered meal-card entrance on day change (subtle), suppressed under reduced-motion.

## Layout / Components

- Mobile-first single column; ≥720px centers content (max ~560px reading column for plan, wider for shopping) and the day-strip becomes a horizontal week rail.
- **Day navigation:** sticky horizontal week strip (Lun–Dom) with the selected day in primary; swipeable.
- **Meal cards:** Desayuno / Comida / Cena, each with title, items+quantities, per-meal macro chips, expandable tip. A "Snacks y antojo" block follows.
- **Day macro bar:** four slim progress bars (P/C/G/Fibra) vs target + kcal total + water/steps reminders.
- **Shopping list:** grouped by category (Proteínas, Verduras…), each item a large checkbox row with exact buy quantity + note. Progress count ("12/38"). State persisted in localStorage. "Reiniciar lista" action.
- Bottom tab bar (mobile): **Plan** · **Compras** · **Guía**. Z-index scale: base → sticky(10) → sheet(30) → toast(40).

## Offline / state

- Self-contained: data inlined (`plan_data.js`), no fetch needed (works from `file://` too).
- `service-worker.js` + `manifest.webmanifest` → installable PWA, full offline when hosted.
- `localStorage`: checked shopping items, selected day, last tab.
