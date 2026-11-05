# WebAssembly (WASM) Hello World

Een minimaal, cross-platform WebAssembly programma dat een "Hello World" popup toont in de browser.

## 🚀 Kenmerken
- **Minimale footprint**: De gecompileerde `hello.wasm` binary is slechts 97 bytes.
- **Cross-platform**: Draait in alle moderne webbrowsers (Chrome, Safari, Firefox, Edge, iOS, Android).
- **Zelfvoorzienend**: Bevat zowel een compilatiescript (`build.py`) als de WebAssembly Text representatie (`hello.wat`).
- **Geautomatiseerde deployment**: Geconfigureerd met GitHub Actions voor automatische publicatie op GitHub Pages.

## 📁 Bestanden in dit project
- `hello.wat` - De WebAssembly broncode in tekstformaat (WAT).
- `build.py` - Python compilatiescript dat de binaire `.wasm` genereert.
- `hello.wasm` - De gecompileerde WebAssembly bytecode (97 bytes).
- `index.html` - De webhost die de WASM-module laadt en de popup triggert.
- `.github/workflows/deploy.yml` - GitHub Actions workflow voor GitHub Pages.

## 🛠️ Lokaal draaien
Open simpelweg `index.html` in je browser, of start een lokale webserver:
```bash
python3 -m http.server 8000
```
Open vervolgens `http://localhost:8000`.

## 📦 Hoe te compileren
Mocht je wijzigingen maken in `hello.wat`, hercompileer dan met:
```bash
python3 build.py
```
