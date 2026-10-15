"""
SmartCube QA - Lanzador del navegador persistente (CDP).

Abre UNA sola vez un Chromium (Playwright) con perfil persistente y un puerto de
depuracion (CDP) abierto, y lo deja corriendo. El REPL de comandos (qa.py) se
conecta a este navegador ya abierto, de modo que se puede actualizar el codigo de
comandos SIN cerrar ni reiniciar el navegador (no se pierde la pagina ni la sesion).

Uso:
    uv run navegador.py            # abre el navegador y lo deja escuchando en CDP

Dejar esta ventana/terminal abierta mientras se trabaja. Para cerrar el navegador,
presionar Ctrl+C aqui (o cerrar la ventana de Chrome).

Detalles:
- Perfil persistente en 05_codigo/.pw-profile/ (la sesion queda guardada).
- Puerto CDP por defecto: 9222 (configurable con la variable CDP_PORT del .env).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
PROFILE_DIR = BASE_DIR / ".pw-profile"


def cargar_config() -> dict:
    load_dotenv(BASE_DIR / ".env")
    url = os.getenv("SMARTCUBE_URL", "").strip().rstrip("/")
    if not url:
        print("ERROR: falta SMARTCUBE_URL en 05_codigo/.env")
        sys.exit(1)
    puerto = os.getenv("CDP_PORT", "9222").strip()
    return {"url": url, "puerto": puerto}


def main() -> None:
    cfg = cargar_config()
    headless = "--headless" in sys.argv
    PROFILE_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        contexto = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
            viewport={"width": 1600, "height": 900},
            args=[f"--remote-debugging-port={cfg['puerto']}"],
        )
        page = contexto.pages[0] if contexto.pages else contexto.new_page()
        page.goto(cfg["url"], wait_until="networkidle")

        print("=" * 60)
        print("Navegador SmartCube abierto y escuchando en CDP.")
        print(f"  URL inicial : {page.url}")
        print(f"  Puerto CDP  : {cfg['puerto']}")
        print("")
        print("Si hay que iniciar sesion, hazlo en la ventana del navegador.")
        print("Deja ESTA terminal abierta. En otra terminal ejecuta:")
        print("    uv run qa.py")
        print("")
        print("Para cerrar el navegador: Ctrl+C aqui o cierra la ventana.")
        print("=" * 60)

        try:
            # Mantener el proceso vivo hasta Ctrl+C o cierre de la ventana.
            page.wait_for_event("close", timeout=0)
        except KeyboardInterrupt:
            print("\nCerrando navegador (Ctrl+C)...")
        except Exception:
            # La ventana se cerro manualmente.
            print("\nLa ventana del navegador se cerro.")
        finally:
            try:
                contexto.close()
            except Exception:
                pass
        print("Navegador cerrado.")


if __name__ == "__main__":
    main()
