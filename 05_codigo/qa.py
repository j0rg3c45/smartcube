"""
SmartCube QA - REPL de comandos conectado por CDP al navegador ya abierto.

Se conecta al Chromium que lanzo 'navegador.py' (puerto CDP) y abre un REPL (qa>)
para navegar, hacer clic, escribir, capturar, etc. Al estar separado del navegador,
este script se puede CERRAR Y VOLVER A LANZAR tras actualizar el codigo SIN perder
la pagina ni la sesion del navegador.

Uso:
    1) En una terminal:   uv run navegador.py   (dejar abierta)
    2) En otra terminal:  uv run qa.py

Comandos del REPL (escribe 'ayuda' dentro de la sesion):
    goto <ruta>           navega a una ruta relativa
    url                   muestra URL y titulo actuales
    click <selector>      clic en elemento (CSS o texto="...")
    type/fill <sel> | <t> escribe en un campo
    press <sel> <Key>     presiona una tecla
    enter <sel>           ENTER en un campo
    wait <ms>             espera milisegundos
    text/count/html <sel> inspeccionar elementos
    rows                  resume filas de la tabla visible

  Flujo de radicados (modulo Asignacion):
    asignacion            navega al modulo de Asignacion
    estado [Estado]       filtra por estado (por defecto 'Asignado')
    radicados             lista radicados visibles ordenados
    detalle <R-...>       abre 'Ver detalle' del radicado
    abrir <R-...>         AUTO: Asignacion -> filtrar Asignado -> abrir detalle
    siguiente             AUTO: abre el radicado MENOR en estado Asignado
    iniciar               pulsa 'Iniciar Tramite' (ACCION CRITICA)

  Wizard "Gestion de Tramites" (parte tecnica):
    agregarfoto           pulsa '+ Agregar foto' (opcional)
    subirfoto <ruta>      carga un archivo de imagen
    continuar             pulsa 'Continuar' para avanzar de paso
    selects               lista los <select> de la pagina con sus opciones e indice
    select <sel> | <opt>  elige una opcion de un <select> (por etiqueta o value)

    cap [etiqueta]        guarda HTML + screenshot
    lote on|off           activa/desactiva confirmacion de acciones criticas
    ayuda                 muestra esta ayuda
    salir                 cierra el REPL (NO cierra el navegador)
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
CAPTURAS_DIR = BASE_DIR / "capturas"

PALABRAS_CRITICAS = ("guardar", "confirmar", "submit", "enviar", "aprobar",
                     "eliminar", "borrar", "crear", "asignar", "iniciar")

_pedir_confirmacion = True


def cargar_config() -> dict:
    load_dotenv(BASE_DIR / ".env")
    url = os.getenv("SMARTCUBE_URL", "").strip().rstrip("/")
    puerto = os.getenv("CDP_PORT", "9222").strip()
    return {"url": url, "puerto": puerto}


def localizar(page, selector: str):
    selector = selector.strip()
    if selector.startswith("texto="):
        return page.get_by_text(selector[len("texto="):].strip(), exact=False)
    return page.locator(selector)


def es_critico(desc: str) -> bool:
    d = desc.lower()
    return any(p in d for p in PALABRAS_CRITICAS)


def confirmar(desc: str) -> bool:
    if not _pedir_confirmacion or not es_critico(desc):
        return True
    r = input(f"  [CONFIRMAR] Accion critica -> {desc}. Escribe 'si' para continuar: ")
    return r.strip().lower() in ("si", "sí", "s", "yes", "y")


def guardar_captura(page, etiqueta: str = "pantalla") -> None:
    CAPTURAS_DIR.mkdir(exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre = f"{marca}_{etiqueta}".replace("/", "_")
    (CAPTURAS_DIR / f"{nombre}.html").write_text(page.content(), encoding="utf-8")
    page.screenshot(path=str(CAPTURAS_DIR / f"{nombre}.png"), full_page=True)
    print(f"  HTML       : {nombre}.html")
    print(f"  Screenshot : {nombre}.png")


def resumir_filas(page) -> None:
    filas = page.locator("table tbody tr")
    total = filas.count()
    print(f"  Filas en tabla: {total}")
    for i in range(min(total, 30)):
        texto = " | ".join(c.strip() for c in filas.nth(i).inner_text().split("\t") if c.strip())
        print(f"   {i+1:>2}. {texto[:160]}")


def mostrar_estado(page) -> None:
    print(f"  URL   : {page.url}")
    try:
        print(f"  Titulo: {page.title()}")
    except Exception:
        pass


def ir_asignacion(page, base_url: str) -> None:
    page.goto(base_url + "/gestion-predial/asignacion", wait_until="networkidle")
    mostrar_estado(page)


def filtrar_estado(page, estado: str = "Asignado") -> None:
    page.get_by_text("Todos los estados", exact=False).first.click()
    page.wait_for_timeout(400)
    etiqueta = page.locator("label", has_text=estado).first
    etiqueta.locator("input[type=checkbox]").check()
    page.wait_for_timeout(300)
    try:
        page.get_by_role("heading", name="Asignación de Radicados").click()
    except Exception:
        page.mouse.click(5, 5)
    page.wait_for_timeout(300)
    page.wait_for_load_state("networkidle")
    print(f"  Filtro de estado aplicado: {estado} (menu cerrado)")


def listar_radicados(page) -> list[str]:
    celdas = page.locator("table tbody tr td:nth-child(2)")
    rads = [celdas.nth(i).inner_text().strip() for i in range(celdas.count())
            if celdas.nth(i).inner_text().strip()]
    return sorted(rads)


def abrir_detalle(page, radicado: str) -> bool:
    # Esperar a que la tabla cargue/recargue antes de buscar (evita falsos
    # "no encontrado" por timing tras aplicar un filtro).
    try:
        page.wait_for_selector("table tbody tr", timeout=5000)
    except Exception:
        pass
    page.wait_for_timeout(500)
    # Buscar la fila cuyo radicado coincide (hasta 2 reintentos por si recarga).
    for intento in range(3):
        filas = page.locator("table tbody tr")
        for i in range(filas.count()):
            fila = filas.nth(i)
            if radicado in fila.inner_text():
                boton = fila.locator('button[title="Ver detalle"], a[title="Ver detalle"]')
                if boton.count() == 0:
                    boton = fila.get_by_text("open_in_new", exact=False)
                boton.first.click()
                page.wait_for_load_state("networkidle")
                mostrar_estado(page)
                return True
        page.wait_for_timeout(700)
    print(f"  No se encontro el radicado {radicado} en la tabla visible.")
    print("  Sugerencia: usa 'radicados' para ver los visibles, o puede estar en la pagina 2.")
    return False


def iniciar_tramite(page) -> None:
    if not confirmar("Iniciar Tramite (cambia el estado del tramite)"):
        print("  Cancelado por el usuario.")
        return
    boton = page.get_by_role("button", name="Iniciar Trámite")
    if boton.count() == 0:
        boton = page.get_by_text("Iniciar Trámite", exact=False)
    boton.first.click()
    page.wait_for_load_state("networkidle")
    print("  'Iniciar Tramite' ejecutado.")
    mostrar_estado(page)


def agregar_foto(page) -> None:
    boton = page.get_by_role("button", name="+ Agregar foto")
    if boton.count() == 0:
        boton = page.get_by_text("Agregar foto", exact=False)
    boton.first.click()
    page.wait_for_timeout(400)
    print("  '+ Agregar foto' pulsado.")


def subir_foto(page, ruta: str) -> None:
    ruta = ruta.strip().strip('"')
    archivo = Path(ruta)
    if not archivo.exists():
        print(f"  No existe el archivo: {ruta}")
        return
    inputs = page.locator("input[type=file]")
    if inputs.count() > 0:
        inputs.first.set_input_files(str(archivo))
        page.wait_for_timeout(600)
        print(f"  Foto cargada en input file: {archivo.name}")
        return
    try:
        with page.expect_file_chooser() as fc_info:
            agregar_foto(page)
        fc_info.value.set_files(str(archivo))
        page.wait_for_timeout(600)
        print(f"  Foto cargada via dialogo: {archivo.name}")
    except Exception as e:
        print(f"  No se pudo cargar la foto: {type(e).__name__}: {e}")


def llenar_direccion(page, vp_valor, vp_letra, vg_valor, vg_letra, num_predio):
    """Llena los campos de texto fijos del modal de nueva direccion.

    Usa los placeholders del formulario para ubicar cada campo. Los desplegables
    (tipo, clase de via) se asumen ya seleccionados. Los complementos/segmentos
    se agregan aparte.
    """
    # Vía principal: Valor (placeholder 'Ej: 10') y Letra (primer 'Ej: A').
    page.locator("input[placeholder='Ej: 10']").first.fill(str(vp_valor))
    letras = page.locator("input[placeholder='Ej: A']")
    letras.nth(0).fill(str(vp_letra))          # letra via principal
    # Vía generadora: Valor (placeholder 'Ej: 5') y Letra (segundo 'Ej: A').
    page.locator("input[placeholder='Ej: 5']").first.fill(str(vg_valor))
    if letras.count() > 1:
        letras.nth(1).fill(str(vg_letra))      # letra via generadora
    # Número del predio (placeholder 'Ej: 42').
    page.locator("input[placeholder='Ej: 42']").first.fill(str(num_predio))
    page.wait_for_timeout(300)
    print(f"  Direccion llenada: VP {vp_valor}{vp_letra} / VG {vg_valor}{vg_letra} / Nro {num_predio}")


def continuar_wizard(page) -> None:
    """Pulsa el boton de avanzar del wizard. El nombre cambia entre pasos:
    'Continuar' (paso 1) o 'Siguiente Paso' (pasos siguientes)."""
    boton = None
    for nombre in ("Siguiente Paso", "Continuar"):
        cand = page.get_by_role("button", name=nombre)
        if cand.count() > 0:
            boton = cand
            break
    if boton is None:
        # Respaldo: boton que contenga alguno de los textos.
        boton = page.locator("button", has_text="Siguiente")
        if boton.count() == 0:
            boton = page.locator("button", has_text="Continuar")
    if boton.count() == 0:
        print("  No se encontro el boton de avanzar (Continuar / Siguiente Paso).")
        return
    boton.first.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(400)
    print("  Boton de avanzar pulsado.")
    mostrar_estado(page)


# --- Secuencias automaticas (varios pasos de una vez) ---

def abrir_radicado(page, base_url: str, radicado: str) -> bool:
    """Secuencia: ir a Asignacion -> filtrar Asignado -> abrir detalle del radicado.

    No ejecuta acciones criticas (solo navega, filtra y abre lectura).
    """
    print(f"  [1/3] Navegando a Asignacion...")
    ir_asignacion(page, base_url)
    print(f"  [2/3] Filtrando por estado Asignado...")
    filtrar_estado(page, "Asignado")
    print(f"  [3/3] Abriendo detalle de {radicado}...")
    return abrir_detalle(page, radicado)


def siguiente_radicado(page, base_url: str) -> str | None:
    """Abre automaticamente el radicado MENOR en estado Asignado.

    Devuelve el radicado abierto, o None si no hay radicados.
    Util para procesar en orden sin escribir el numero cada vez.
    """
    ir_asignacion(page, base_url)
    filtrar_estado(page, "Asignado")
    rads = listar_radicados(page)
    if not rads:
        print("  No hay radicados en estado Asignado.")
        return None
    menor = rads[0]
    print(f"  Radicado menor en Asignado: {menor} (de {len(rads)})")
    abrir_detalle(page, menor)
    return menor


def conectar(cfg: dict):
    """Conecta por CDP al navegador ya abierto por navegador.py."""
    p = sync_playwright().start()
    endpoint = f"http://localhost:{cfg['puerto']}"
    try:
        browser = p.chromium.connect_over_cdp(endpoint)
    except Exception as e:
        print(f"ERROR: no se pudo conectar al navegador en {endpoint}.")
        print("Asegurate de haber lanzado antes 'uv run navegador.py'.")
        print(f"Detalle: {type(e).__name__}: {e}")
        p.stop()
        sys.exit(1)
    contexto = browser.contexts[0] if browser.contexts else browser.new_context()
    # Elegir una pagina real de la app, ignorando pestañas de DevTools / internas.
    page = None
    for pg in contexto.pages:
        u = (pg.url or "")
        if u.startswith("devtools://") or u.startswith("chrome://") or u.startswith("about:"):
            continue
        page = pg
        break
    if page is None:
        page = contexto.pages[0] if contexto.pages else contexto.new_page()
    return p, browser, page


def repl(page, base_url: str) -> None:
    global _pedir_confirmacion
    print("\n=== REPL SmartCube QA (conectado por CDP) ===")
    print("Escribe 'ayuda' para ver comandos, 'salir' para cerrar el REPL.")
    print("(Salir NO cierra el navegador.)")
    mostrar_estado(page)

    while True:
        try:
            linea = input("\nqa> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo del REPL (el navegador sigue abierto)...")
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
                print(f"  Confirmacion de acciones criticas: "
                      f"{'DESACTIVADA' if not _pedir_confirmacion else 'ACTIVA'}")
            elif cmd == "goto":
                destino = base_url + "/" + arg.lstrip("/") if arg else base_url
                page.goto(destino, wait_until="networkidle")
                mostrar_estado(page)
            elif cmd == "url":
                mostrar_estado(page)
            elif cmd == "pestanas":
                ctx = page.context
                print(f"  Pestañas abiertas ({len(ctx.pages)}):")
                for idx, pg in enumerate(ctx.pages):
                    print(f"   [{idx}] {pg.url}")
            elif cmd == "click":
                if confirmar(f"click en '{arg}'"):
                    localizar(page, arg).first.click()
                    page.wait_for_load_state("networkidle")
                    mostrar_estado(page)
            elif cmd in ("type", "fill"):
                sel, _, txt = arg.partition("|")
                loc = localizar(page, sel.strip())
                if confirmar(f"escribir en '{sel.strip()}'"):
                    (loc.first.fill if cmd == "fill" else loc.first.type)(txt.strip())
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
            elif cmd == "asignacion":
                ir_asignacion(page, base_url)
            elif cmd == "estado":
                filtrar_estado(page, arg or "Asignado")
            elif cmd == "radicados":
                rads = listar_radicados(page)
                print(f"  Radicados visibles ({len(rads)}): {', '.join(rads)}")
            elif cmd == "detalle":
                if not arg:
                    print("  Uso: detalle <numero de radicado>")
                else:
                    abrir_detalle(page, arg)
            elif cmd == "abrir":
                if not arg:
                    print("  Uso: abrir <numero de radicado>")
                else:
                    abrir_radicado(page, base_url, arg)
            elif cmd == "siguiente":
                siguiente_radicado(page, base_url)
            elif cmd == "iniciar":
                iniciar_tramite(page)
            elif cmd == "agregarfoto":
                agregar_foto(page)
            elif cmd == "subirfoto":
                if not arg:
                    print("  Uso: subirfoto <ruta del archivo de imagen>")
                else:
                    subir_foto(page, arg)
            elif cmd == "continuar":
                continuar_wizard(page)
            elif cmd == "direccion":
                # Uso: direccion <vpValor> <vpLetra> <vgValor> <vgLetra> <numPredio>
                partes_dir = arg.split()
                if len(partes_dir) < 5:
                    print("  Uso: direccion <vpValor> <vpLetra> <vgValor> <vgLetra> <numPredio>")
                    print("  Ej:  direccion 21 AS 21 A 11")
                else:
                    llenar_direccion(page, *partes_dir[:5])
            elif cmd == "select":
                # Uso: select <selector> | <texto o value de la opcion>
                sel, _, opt = arg.partition("|")
                sel = sel.strip(); opt = opt.strip()
                loc = localizar(page, sel)
                try:
                    loc.first.select_option(label=opt)
                    print(f"  Seleccionado por etiqueta: {opt!r}")
                except Exception:
                    loc.first.select_option(value=opt)
                    print(f"  Seleccionado por value: {opt!r}")
                page.wait_for_timeout(300)
            elif cmd == "selects":
                # Lista todos los <select> de la pagina con sus opciones (para ubicarlos)
                selects = page.locator("select")
                print(f"  Hay {selects.count()} desplegables:")
                for i in range(selects.count()):
                    opts = selects.nth(i).locator("option")
                    textos = [opts.nth(j).inner_text().strip() for j in range(min(opts.count(), 6))]
                    print(f"   [{i}] opciones: {textos}")
            elif cmd == "cap":
                guardar_captura(page, arg or "pantalla")
            elif cmd == "html":
                print((localizar(page, arg).first.inner_html()[:4000]) if arg
                      else page.content()[:4000])
            else:
                print(f"  Comando no reconocido: {cmd}. Escribe 'ayuda'.")
        except Exception as e:
            print(f"  [ERROR] {type(e).__name__}: {e}")
            print("  (Revisa el selector o el estado de la pagina.)")


def main() -> None:
    cfg = cargar_config()
    p, browser, page = conectar(cfg)
    try:
        repl(page, cfg["url"])
    finally:
        # NO cerramos el navegador: solo soltamos la conexion de Playwright.
        try:
            p.stop()
        except Exception:
            pass
    print("REPL cerrado. El navegador sigue abierto.")


if __name__ == "__main__":
    main()
