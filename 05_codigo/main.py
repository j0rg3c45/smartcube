"""
SmartCube QA - Sesion interactiva sobre la plataforma catastral (Playwright).

Abre la plataforma en un navegador controlado usando un perfil persistente
(la sesion queda guardada tras el primer login manual) y entra en un modo
interactivo (REPL) donde se ejecutan comandos: navegar, hacer clic, escribir en
campos, presionar teclas, capturar HTML/screenshot, etc.

MODO CONSERVADOR:
- Las acciones que pueden guardar/confirmar/eliminar piden confirmacion antes
  de ejecutarse (teclea 'si' para confirmar). Se pueden desactivar con 'lote on'
  cuando el usuario autorice ejecucion en lote.
- Nada se envia automaticamente: solo se actua ante un comando explicito.

Uso:
    uv run main.py            # abre navegador con perfil y entra al modo interactivo
    uv run main.py --headless # sin ventana visible (no recomendado para login)

Comandos del REPL (escribe 'ayuda' para verlos dentro de la sesion):
    goto <ruta>           navega a una ruta relativa (ej: goto /gestion-predial/asignacion)
    url                   muestra la URL y el titulo actuales
    click <selector>      hace clic en el elemento (CSS o texto="...")
    type <selector> | <texto>   escribe texto en un campo
    press <selector> <Key>      presiona una tecla (ej: press input Enter)
    enter <selector>      atajo de 'press <selector> Enter'
    fill <selector> | <texto>   limpia y escribe en un campo
    wait <ms>             espera milisegundos
    text <selector>       imprime el texto de un elemento
    count <selector>      cuenta cuantos elementos coinciden
    rows                  resume filas de la primera tabla visible
    cap [etiqueta]        guarda HTML + screenshot de la pantalla actual
    html [selector]       imprime HTML (de la pagina o de un selector)
    lote on|off           activa/desactiva confirmacion para acciones criticas
    ayuda                 muestra esta ayuda
    salir                 cierra el navegador y termina
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
PROFILE_DIR = BASE_DIR / ".pw-profile"
CAPTURAS_DIR = BASE_DIR / "capturas"

# Palabras que marcan una accion como critica (requiere confirmacion).
PALABRAS_CRITICAS = ("guardar", "confirmar", "submit", "enviar", "aprobar",
                     "eliminar", "borrar", "crear", "asignar")

# Estado de confirmacion para acciones criticas (True = pide confirmacion).
_pedir_confirmacion = True


def cargar_url() -> str:
    load_dotenv(BASE_DIR / ".env")
    url = os.getenv("SMARTCUBE_URL", "").strip()
    if not url:
        print("ERROR: falta SMARTCUBE_URL en 05_codigo/.env")
        sys.exit(1)
    return url.rstrip("/")


def localizar(page, selector: str):
    """Devuelve un Locator. Soporta 'texto=...' para buscar por texto visible."""
    selector = selector.strip()
    if selector.startswith("texto="):
        return page.get_by_text(selector[len("texto="):].strip(), exact=False)
    return page.locator(selector)


def es_critico(descripcion: str) -> bool:
    desc = descripcion.lower()
    return any(p in desc for p in PALABRAS_CRITICAS)


def confirmar(descripcion: str) -> bool:
    """Pide confirmacion si la accion es critica y el modo lo exige."""
    if not _pedir_confirmacion or not es_critico(descripcion):
        return True
    resp = input(f"  [CONFIRMAR] Accion critica -> {descripcion}. Escribe 'si' para continuar: ")
    return resp.strip().lower() in ("si", "sí", "s", "yes", "y")


def guardar_captura(page, etiqueta: str = "pantalla") -> None:
    CAPTURAS_DIR.mkdir(exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre = f"{marca}_{etiqueta}".replace("/", "_")
    html_path = CAPTURAS_DIR / f"{nombre}.html"
    png_path = CAPTURAS_DIR / f"{nombre}.png"
    html_path.write_text(page.content(), encoding="utf-8")
    page.screenshot(path=str(png_path), full_page=True)
    print(f"  HTML       : {html_path.name}")
    print(f"  Screenshot : {png_path.name}")


def resumir_filas(page) -> None:
    """Resume las filas de la primera tabla visible (util para listados)."""
    filas = page.locator("table tbody tr")
    total = filas.count()
    print(f"  Filas en tabla: {total}")
    for i in range(min(total, 30)):
        texto = " | ".join(
            c.strip() for c in filas.nth(i).inner_text().split("\t") if c.strip()
        )
        print(f"   {i+1:>2}. {texto[:160]}")


def mostrar_estado(page) -> None:
    print(f"  URL   : {page.url}")
    try:
        print(f"  Titulo: {page.title()}")
    except Exception:
        pass


def repl(page, base_url: str) -> None:
    global _pedir_confirmacion
    print("\n=== Sesion interactiva SmartCube QA ===")
    print("Escribe 'ayuda' para ver comandos, 'salir' para terminar.")
    mostrar_estado(page)

    while True:
        try:
            linea = input("\nqa> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break
        if not linea:
            continue

        partes = linea.split(" ", 1)
        cmd = partes[0].lower()
        arg = partes[1].strip() if len(partes) > 1 else ""

        try:
            if cmd == "salir":
                break
            elif cmd == "ayuda":
                print(__doc__)
            elif cmd == "lote":
                _pedir_confirmacion = (arg.lower() != "on")
                estado = "DESACTIVADA" if not _pedir_confirmacion else "ACTIVA"
                print(f"  Confirmacion de acciones criticas: {estado}")
            elif cmd == "goto":
                destino = base_url + "/" + arg.lstrip("/") if arg else base_url
                page.goto(destino, wait_until="networkidle")
                mostrar_estado(page)
            elif cmd == "url":
                mostrar_estado(page)
            elif cmd == "click":
                if confirmar(f"click en '{arg}'"):
                    localizar(page, arg).first.click()
                    page.wait_for_load_state("networkidle")
                    mostrar_estado(page)
            elif cmd in ("type", "fill"):
                sel, _, txt = arg.partition("|")
                loc = localizar(page, sel.strip())
                if confirmar(f"escribir en '{sel.strip()}'"):
                    if cmd == "fill":
                        loc.first.fill(txt.strip())
                    else:
                        loc.first.type(txt.strip())
                    print(f"  Escrito en {sel.strip()}: {txt.strip()!r}")
            elif cmd == "press":
                sel, _, key = arg.rpartition(" ")
                localizar(page, sel.strip()).first.press(key.strip())
                page.wait_for_load_state("networkidle")
                mostrar_estado(page)
            elif cmd == "enter":
                localizar(page, arg).first.press("Enter")
                page.wait_for_load_state("networkidle")
                mostrar_estado(page)
            elif cmd == "wait":
                page.wait_for_timeout(int(arg or "500"))
            elif cmd == "text":
                print("  " + localizar(page, arg).first.inner_text())
            elif cmd == "count":
                print(f"  Coincidencias: {localizar(page, arg).count()}")
            elif cmd == "rows":
                resumir_filas(page)
            elif cmd == "cap":
                guardar_captura(page, arg or "pantalla")
            elif cmd == "html":
                if arg:
                    print(localizar(page, arg).first.inner_html()[:4000])
                else:
                    print(page.content()[:4000])
            else:
                print(f"  Comando no reconocido: {cmd}. Escribe 'ayuda'.")
        except Exception as e:
            print(f"  [ERROR] {type(e).__name__}: {e}")
            print("  (Revisa el selector o el estado de la pagina.)")


def main() -> None:
    headless = "--headless" in sys.argv
    base_url = cargar_url()
    PROFILE_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        contexto = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
            viewport={"width": 1600, "height": 900},
        )
        page = contexto.pages[0] if contexto.pages else contexto.new_page()
        print(f"Abriendo: {base_url}")
        page.goto(base_url, wait_until="networkidle")

        if "login" in page.url.lower() or page.locator("input[type=password]").count() > 0:
            print("\n--- Parece que hay que iniciar sesion ---")
            print("Inicia sesion en la ventana del navegador y luego vuelve aqui.")
            print("La sesion quedara guardada en el perfil para la proxima vez.")

        repl(page, base_url)
        contexto.close()
        print("Navegador cerrado.")


if __name__ == "__main__":
    main()
