# Antigravity Project Richtlijnen & UI Voorkeuren - Brandstof Informatie

Deze richtlijnen gelden voor alle huidige en toekomstige aanpassingen in deze applicatie.

## 1. UI & Design Standaard: "Smooth, Donker & Nooit Lomp of Wit Vierkant"
- **Geen grote witte of vierkante blokken:** Gebruik dark glassmorphism (`rgba(11, 15, 25, 0.90)`, `backdrop-filter: blur()`, subtiele borders).
- **Afgeronde vormen:** Badges, filters en labels hebben altijd afgeronde pil-vormen.
- **Smartphone & Tablet:** Volledig geoptimaliseerd voor touch, 1-focus intent ("KISS"), touch targets $\ge 44$px.

## 2. Postcode & Plaatsnaam Conventie (Altijd Samen)
- **Postcode + Plaatsnaam:** Toon bij postcodes altijd direct de plaatsnaam (bv. "3511 Utrecht" in plaats van alleen een losse 4-cijferige code).
- **Zoekondersteuning:** Herken zowel losse postcodes ("3511", "3511 AA"), combinaties ("3511 Utrecht", "7312 Apeldoorn") als plaatsnamen ("Utrecht", "Apeldoorn").
- **Kaarten & Winnaar-badges:** Vermeld altijd `3511 Utrecht` duidelijk op de station- en winnaarskaarten.

## 3. Directe Feedback & Valideren van Data
- **Knoppen feedback (Click/Tick):** Informeer de gebruiker direct met status en aantal verkregen resultaten (bv. "✓ 14 stations gevonden binnen 10 km").
- **Datavalidatie in de UI:** Toon transparant de bron en validatiestatus van de brandstofprijzen en GPS-positie.
- **Leesbaarheid:** Geen afgekipte teksten, soepel scrollen in lijsten (`-webkit-overflow-scrolling: touch`).

## 4. Deployment & GitHub Online Standaard: Alleen Online via GitHub
- Niet meer lokaal testen, direct online via GitHub Pages en GitHub Actions.
- Automatische live update via `version.json`.
