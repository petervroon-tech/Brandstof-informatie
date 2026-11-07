# Brandstof-informatie v2.2.0

Een interactief, cross-platform WebAssembly dashboard voor **Brandstof-informatie in Nederland**: actuele dagprijzen én het dagelijkse prijsverschil met de dag ervoor voor **Super (Euro 95 E10 & Super 98 E5)** en **Diesel (B7)** in **91 plaatsen (178 tankstations)** door heel Nederland (alle 12 provincies).

**Auteur:** Peter Vroon  
**Versie:** 2.2.0

## 🚀 Kenmerken
- **🔄 Volautomatische Dagelijkse Prijsupdater (GitHub Actions)**:
  - Elke ochtend om 06:00 UTC (07:00 / 08:00 Nederlandse tijd) draait de geautomatiseerde cronjob `.github/workflows/daily-price-update.yml`.
  - Berekent en ververst de actuele marktprijzen en dagmutaties t.o.v. de dag ervoor voor alle 178 tankstations.
  - Hercompileert automatisch de WebAssembly-binary (`hello.wasm`), updatet `index.html` en publiceert direct via GitHub Pages.
  - Kan desgewenst ook op elk moment handmatig worden gestart via de GitHub Actions interface met de knop **"Run workflow"**.
- **📱 Multi-Device Geoptimaliseerd (iPhone, iPad & MacBook)**:
  - **iPhone (Staand & Liggend)**: Geen horizontale scrollbars meer; de hele lay-out sluit 100% aan op het scherm. Brede tabellen transformeren automatisch in strakke, compacte stationskaarten met een 3-koloms prijsraster. Inclusief zwevende duim-navigatiebalk onderaan en bottom-sheet Google Maps routeplanner.
  - **iPad & Tablets**: Evenwichtige lay-out (2-koloms filters, ruimere grafiekweergave en soepele aanraakbediening).
  - **MacBook & Desktop**: Professioneel dashboard met gecentreerde weergave (max 1180px), overzichtelijke 4-koloms statistiekenbalk en een complete 7-koloms tabel met routeplanner- en trendknoppen.
- **WebAssembly Power**: De complete landelijke dataset (178 stations in 91 steden en dorpen inclusief dagprijzen, GPS-coördinaten, postcodes en dagverschillen) wordt rechtstreeks vanuit het lineaire geheugen van de WebAssembly-binary (`hello.wasm`) gedecodeerd.
- **🎯 Goedkoopste Tankstation in Instelbare Cirkel rond Postcode**:
  - Voer eenvoudig een **4-cijferige postcode** (bijv. `7311`, `1012`, `3011`) of plaatsnaam in, of gebruik de knop **"📍 GPS"** voor je huidige positie.
  - Stel de gewenste **zoekstraal (cirkel in km)** in met de soepele schuifregelaar (1 t/m 50 km) of kies met één klik een snelle preset: **3 km, 5 km, 10 km, 15 km, 25 km of 50 km**.
  - Kies de gewenste brandstof (**Euro 95 E10, Diesel B7 of Super 98 E5**).
  - De applicatie berekent met de **Haversine-afstandsformule** direct de exacte afstand (vogelvlucht) naar elk station en presenteert de **🏆 Winnaar (Nr. 1 Goedkoopste Tankstation in de cirkel)** in een opvallende goud/groene banner inclusief berekende besparing per liter en op een volle tank van 50 liter.
  - Alle tankstations in de cirkel worden getoond met een afstandsbadge (`📍 X.X km`) en gesorteerd op de laagste prijs of op afstand.
  - Start vanaf de winnaar direct de **Google Maps Routeplanner** of bekijk zijn historische prijstrend.
- **Prijsverschil met gisteren**: Onder elke prijs staat direct een visuele badge:
  - 🟢 **▼ -0.015**: Prijs gedaald t.o.v. gisteren (goedkoper).
  - 🔴 **▲ +0.010**: Prijs gestegen t.o.v. gisteren (duurder).
  - ⚪ **= 0.000**: Prijs ongewijzigd.
- **Dynamisch Filter op Plaats**: Het dropdown-menu vult zich automatisch met alle 91 unieke plaatsen in Nederland (op alfabetische volgorde van Alkmaar en Apeldoorn tot Zwolle), plus een overzicht voor heel Nederland.
- **Live Zoeken & Sorteren**: Sorteer op goedkoopste Euro 95, Diesel of Super 98, óf sorteer op de **sterkste dalers** om direct de grootste prijsdalingen te vinden.
- **Statistieken Banner**: Toont direct de laagste prijs en de bijbehorende dagontwikkeling voor Euro 95, Super 98 en Diesel binnen de gekozen plaats.
- **Flexibel Instelbare Trendgrafiek (Lijngrafiek) — Landelijk, per Plaats én per Tankstation**:
  - **Prijsverloop per Tankstation**: Kies in de grafiek elk willekeurig tankstation (of klik op **"📈 Trend"** in de tabel of in de Google Maps pop-up) om het specifieke prijsverloop van dat tankstation over de tijd te zien, inclusief vergelijking met het landelijk gemiddelde (met optionele referentiestippellijn).
  - Stel **volledig zelf de gewenste periode in** met interactieve schuifbalken en snelle presets:
    - 📅 **Per Week**: Kies zelf het gewenste aantal weken (1 t/m 52 weken, bijv. 1 wk, 2 wk, 4 wk, 12 wk) met live schuifbalk en datumbereik.
    - 🗓️ **Per Maand**: Kies zelf het aantal maanden (1 t/m 83 maanden, bijv. 1 mnd, 3 mnd, 6 mnd, 12 mnd, 24 mnd of alles 2020-2026).
    - 📊 **Per Jaar**: Kies zelf het begin- en eindjaar (bijv. 2021-2023, 2024-2026 of de volledige historie 2020-2026) inclusief historische mijlpalen (coronacrisis dip, energiecrisis piek en accijnsverlagingen).
    - ⚙️ **Aangepaste Datumreeks**: Kies met datumkiezers letterlijk elke gewenste begindatum en einddatum.
  - Aan/uit schakelbare lijnen per brandstof (Euro 95 E10, Super 98 E5, Diesel B7).
  - Interactieve tooltip met richtkruis, exacte stationsprijzen en landelijke benchmarkvergelijking.
- **Google Maps & Routeplanner**: Klik op een willekeurig tankstation of op de knop **"🗺️ Kaart & Route"** (of een van de goedkoopste stations in de statistiekenbalk) om direct:
  - Een interactieve **Google Maps kaart** van het tankstation te bekijken.
  - Met één klik de **Google Maps Routeplanner** te starten (op desktop of mobiel) naar het adres van het tankstation.
- **Geautomatiseerde deployment**: Direct gekoppeld aan GitHub Pages via GitHub Actions.

## 📁 Bestanden in dit project
- `hello.wat` - De WebAssembly broncode in tekstformaat (WAT).
- `build.py` - Compilatiescript met de landelijke dataset, dagverschilberekeningen en historische trends.
- `hello.wasm` - De gecompileerde WebAssembly binary (85.222 bytes).
- `index.html` - De interactieve webapp.
- `.github/workflows/deploy.yml` - GitHub Actions workflow voor GitHub Pages.

## 🛠️ Lokaal bekijken
Open simpelweg `index.html` in je browser:
```bash
open index.html
```
