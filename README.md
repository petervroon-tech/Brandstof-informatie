# Brandstofprijzen Nederland (WebAssembly)

Een interactief, cross-platform WebAssembly dashboard dat actuele dagprijzen toont voor **Super (Euro 95 E10 & Super 98 E5)** en **Diesel (B7)** bij tankstations in Nederland, met een direct filter op plaats (waaronder Apeldoorn).

## 🚀 Kenmerken
- **WebAssembly Power**: De complete dataset met brandstofprijzen en metadata wordt direct gedecodeerd vanuit het lineaire geheugen van de gecompileerde `hello.wasm` binary.
- **Interactieve Filters**:
  - Filter op plaats/stad (standaard **Apeldoorn**, plus Arnhem, Deventer, Utrecht, Amsterdam, Rotterdam, Zwolle en Landelijk).
  - Sorteer direct op goedkoopste Euro 95, Diesel, Super 98 of alfabetisch op naam.
  - Live zoekbalk op stationnaam of straatnaam.
- **Statistieken Banner**: Toont realtime de laagste prijzen en voordeligste stations binnen de geselecteerde plaats.
- **Geautomatiseerde deployment**: Direct gekoppeld aan GitHub Pages via GitHub Actions.

## 📁 Bestanden in dit project
- `hello.wat` - De WebAssembly broncode in tekstformaat (WAT).
- `build.py` - Python compilatiescript dat de binaire `.wasm` genereert inclusief de dataset.
- `hello.wasm` - De gecompileerde WebAssembly binary.
- `index.html` - De webhost met het interactieve dashboard.
- `.github/workflows/deploy.yml` - GitHub Actions workflow voor continue publicatie naar GitHub Pages.

## 🛠️ Lokaal bekijken
Open simpelweg `index.html` in je browser:
```bash
open index.html
```

## 📦 Hoe te hercompileren
Als je prijzen of stations toevoegt aan `build.py`, hercompileer dan met:
```bash
python3 build.py
```
