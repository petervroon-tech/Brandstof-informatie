# Brandstofprijzen Nederland (WebAssembly)

Een interactief, cross-platform WebAssembly dashboard dat actuele dagprijzen toont voor **Super (Euro 95 E10 & Super 98 E5)** en **Diesel (B7)** in **91 plaatsen (178 tankstations)** door heel Nederland (alle 12 provincies).

## 🚀 Kenmerken
- **WebAssembly Power**: De complete landelijke dataset (178 stations in 91 steden en dorpen) wordt rechtstreeks vanuit het lineaire geheugen van de WebAssembly-binary (`hello.wasm`) gedecodeerd.
- **Dynamisch Filter op Plaats**: Het dropdown-menu vult zich automatisch met alle 91 unieke plaatsen in Nederland (op alfabetische volgorde van Alkmaar en Apeldoorn tot Zwolle), plus een overzicht voor heel Nederland.
- **Live Zoeken & Sorteren**: Zoek op plaats, straat of merk (Fieten Olie, TinQ, Tango, Shell, BP, Esso, AVIA) en sorteer op de voordeligste prijs.
- **Statistieken Banner**: Toont direct de laagste prijs voor Euro 95, Super 98 en Diesel binnen de gekozen plaats.
- **Geautomatiseerde deployment**: Direct gekoppeld aan GitHub Pages via GitHub Actions.

## 📁 Bestanden in dit project
- `hello.wat` - De WebAssembly broncode in tekstformaat (WAT).
- `build.py` - Compilatiescript met de landelijke dataset (12 provincies).
- `hello.wasm` - De gecompileerde WebAssembly binary (24.741 bytes).
- `index.html` - De interactieve webapp.
- `.github/workflows/deploy.yml` - GitHub Actions workflow voor GitHub Pages.

## 🛠️ Lokaal bekijken
Open simpelweg `index.html` in je browser:
```bash
open index.html
```
