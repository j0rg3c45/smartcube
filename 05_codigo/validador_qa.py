"""
SmartCube QA - Validador automatico en lote (tecnica + juridica).

Script autonomo que se conecta por CDP al navegador ya abierto por navegador.py
(sesion persistente, sin credenciales en codigo) y ejecuta, de corrido y sin
intervencion manual, las validaciones tecnica y juridica de los radicados que se le
indiquen. Para cada radicado: lo busca por el buscador (evita el bug de paginacion),
abre el detalle, lee datos clave (tipo de tramite, NPN, propietario), valida la
estructura del NPN, aprueba la validacion tecnica y la juridica, y registra el
resultado. Al final genera un reporte consolidado (CSV) y un log, y guarda capturas
de evidencia.

Requisitos (ya instalados en el proyecto con uv):
    playwright, python-dotenv
    uv run playwright install chromium   (una sola vez)

Configuracion (05_codigo/.env):
    SMARTCUBE_URL   = https://jamundi-dev.smartcubescol.com/
    CDP_PORT        = 9222   (mismo puerto que usa navegador.py)

Uso:
    1) En una terminal:  uv run navegador.py      (dejar abierta; iniciar sesion una vez)
    2) En otra terminal:
         uv run validador_qa.py R-2026-0062 R-2026-0067 R-2026-0079
       o para validar TODOS los que esten en estado Asignado con validacion pendiente:
         uv run validador_qa.py --todos
    3) (Opcional) ver qué haría sin aprobar nada:
         uv run validador_qa.py --todos --dry-run

Salidas (en 05_codigo/):
    reportes/validaciones_<fecha>.csv   reporte consolidado
    reportes/validaciones_<fecha>.log   log detallado
    capturas/val_<radicado>_*.png       evidencias por radicado
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

BASE_DIR = Path(__file__).resolve().parent
CAPTURAS_DIR = BASE_DIR / "capturas"
REPORTES_DIR = BASE_DIR / "reportes"

OBS_TECNICA = "Todo esta Ok"
OBS_JURIDICA = "Todo esta Ok en Juridica"


# ---------------------------------------------------------------------------
# Utilidades de configuracion, log y reporte
# ---------------------------------------------------------------------------

def cargar_config() -> dict:
    load_dotenv(BASE_DIR / ".env")
    url = os.getenv("SMARTCUBE_URL", "").strip().rstrip("/")
    puerto = os.getenv("CDP_PORT", "9222").strip()
    if not url:
        print("ERROR: falta SMARTCUBE_URL en 05_codigo/.env")
        sys.exit(1)
    return {"url": url, "puerto": puerto}


class Reporte:
    """Acumula resultados y los vuelca a CSV + log."""

    def __init__(self) -> None:
        REPORTES_DIR.mkdir(exist_ok=True)
        marca = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_path = REPORTES_DIR / f"validaciones_{marca}.csv"
        self.log_path = REPORTES_DIR / f"validaciones_{marca}.log"
        self.filas: list[dict] = []
        self._log = self.log_path.open("w", encoding="utf-8")

    def log(self, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        linea = f"[{ts}] {msg}"
        print(linea)
        self._log.write(linea + "\n")
        self._log.flush()

    def agregar(self, fila: dict) -> None:
        self.filas.append(fila)

    def cerrar(self) -> None:
        if self.filas:
            campos = ["radicado", "tipo_tramite", "npn", "npn_longitud",
                      "npn_valido", "propietario", "resultado", "hallazgos"]
            with self.csv_path.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=campos)
                w.writeheader()
                for fila in self.filas:
                    w.writerow({k: fila.get(k, "") for k in campos})
            self.log(f"Reporte CSV: {self.csv_path}")
        self.log(f"Log: {self.log_path}")
        self._log.close()


# ---------------------------------------------------------------------------
# Validacion de reglas tecnicas (alfanumericas) sin tocar la plataforma
# ---------------------------------------------------------------------------

def validar_npn(npn: str) -> tuple[bool, str]:
    """Valida la estructura basica del NPN (30 digitos numericos).
    Devuelve (es_valido, detalle)."""
    npn = (npn or "").strip()
    if not npn:
        return False, "NPN vacio"
    if not npn.isdigit():
        return False, f"NPN no numerico: {npn!r}"
    if len(npn) != 30:
        return False, f"NPN con {len(npn)} digitos (oficial 30)"
    return True, "NPN de 30 digitos, estructura basica correcta"


# ---------------------------------------------------------------------------
# Interaccion con la plataforma
# ---------------------------------------------------------------------------

def conectar(cfg: dict):
    p = sync_playwright().start()
    endpoint = f"http://localhost:{cfg['puerto']}"
    try:
        browser = p.chromium.connect_over_cdp(endpoint)
    except Exception as e:
        print(f"ERROR: no se pudo conectar al navegador en {endpoint}.")
        print("Lanza antes: uv run navegador.py")
        print(f"Detalle: {type(e).__name__}: {e}")
        p.stop()
        sys.exit(1)
    contexto = browser.contexts[0] if browser.contexts else browser.new_context()
    page = None
    for pg in contexto.pages:
        u = pg.url or ""
        if u.startswith(("devtools://", "chrome://", "about:")):
            continue
        page = pg
        break
    if page is None:
        page = contexto.pages[0] if contexto.pages else contexto.new_page()
    return p, browser, page


def ir_asignacion(page, base_url: str) -> None:
    page.goto(base_url + "/gestion-predial/asignacion", wait_until="networkidle")
    page.wait_for_timeout(600)


def buscar_radicado(page, radicado: str) -> bool:
    """Escribe el radicado en el buscador y espera a que la tabla lo muestre.
    Evita el problema de paginacion. Devuelve True si aparece la fila."""
    buscador = page.locator("input[placeholder*='Buscar por radicado']")
    if buscador.count() == 0:
        return False
    buscador.first.fill("")
    buscador.first.type(radicado, delay=20)
    page.wait_for_timeout(1500)
    page.wait_for_load_state("networkidle")
    filas = page.locator("table tbody tr")
    for i in range(filas.count()):
        if radicado in filas.nth(i).inner_text():
            return True
    return False


def abrir_detalle(page, radicado: str) -> bool:
    filas = page.locator("table tbody tr")
    for i in range(filas.count()):
        fila = filas.nth(i)
        if radicado in fila.inner_text():
            boton = fila.locator('button[title="Ver detalle"], a[title="Ver detalle"]')
            if boton.count() == 0:
                boton = fila.get_by_text("open_in_new", exact=False)
            boton.first.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(800)
            return True
    return False


def leer_datos_detalle(page) -> dict:
    """Lee datos clave del detalle del radicado."""
    datos = {"tipo_tramite": "", "npn": "", "propietario": ""}
    try:
        texto = page.locator("body").inner_text()
    except Exception:
        texto = ""
    # Tipo de tramite: linea con "Mutacion"/"Rectificaciones"/"Efectos"
    for linea in texto.splitlines():
        l = linea.strip()
        if any(k in l for k in ("Mutación", "Rectificaciones", "Efectos")) and "-" in l:
            datos["tipo_tramite"] = l.split("—")[0].strip()
            break
    # NPN: primera secuencia de 30 digitos
    import re
    m = re.search(r"\b(\d{30})\b", texto)
    if m:
        datos["npn"] = m.group(1)
    else:
        m2 = re.search(r"\b(\d{25,34})\b", texto)  # por si no son 30 exactos
        if m2:
            datos["npn"] = m2.group(1)
    return datos


def estado_validaciones(page) -> dict:
    """Devuelve el estado textual de Validacion Tecnica y Juridica."""
    texto = page.locator("body").inner_text()
    est = {"tecnica": "?", "juridica": "?"}
    # Heuristica simple por bloques
    if "Validación Técnica" in texto:
        bloque = texto.split("Validación Técnica", 1)[1][:120]
        est["tecnica"] = "Aprobado" if "Aprobado" in bloque else (
            "Pendiente" if "Pendiente" in bloque else "?")
    if "Validación Jurídica" in texto:
        bloque = texto.split("Validación Jurídica", 1)[1][:120]
        est["juridica"] = "Aprobado" if "Aprobado" in bloque else (
            "Pendiente" if "Pendiente" in bloque else "?")
    return est


def aprobar_validacion(page, observacion: str, dry_run: bool) -> bool:
    """Pulsa 'Realizar Validacion', escribe observacion y aprueba. En dry-run solo
    abre el modal y cancela."""
    boton = page.get_by_role("button", name="Realizar Validación")
    if boton.count() == 0:
        return False
    boton.first.click()
    page.wait_for_timeout(700)
    ta = page.locator("textarea[placeholder='Observaciones opcionales...']")
    if ta.count() == 0:
        ta = page.locator("textarea")
    if ta.count() > 0:
        ta.first.fill(observacion)
    if dry_run:
        cancelar = page.get_by_role("button", name="Cancelar")
        if cancelar.count() > 0:
            cancelar.first.click()
        page.wait_for_timeout(400)
        return True
    aprobar = page.get_by_role("button", name="Aprobar")
    if aprobar.count() == 0:
        aprobar = page.locator("button", has_text="Aprobar")
    aprobar.first.click()
    page.wait_for_timeout(1500)
    page.wait_for_load_state("networkidle")
    return True


def capturar(page, etiqueta: str) -> None:
    CAPTURAS_DIR.mkdir(exist_ok=True)
    marca = datetime.now().strftime("%H%M%S")
    png = CAPTURAS_DIR / f"val_{etiqueta}_{marca}.png"
    try:
        page.screenshot(path=str(png), full_page=True)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Flujo principal por radicado
# ---------------------------------------------------------------------------

def procesar_radicado(page, base_url: str, radicado: str, rep: Reporte,
                      dry_run: bool) -> None:
    fila = {"radicado": radicado, "tipo_tramite": "", "npn": "", "npn_longitud": "",
            "npn_valido": "", "propietario": "", "resultado": "", "hallazgos": ""}
    hallazgos = []
    rep.log(f"=== {radicado} ===")
    try:
        ir_asignacion(page, base_url)
        if not buscar_radicado(page, radicado):
            fila["resultado"] = "NO ENCONTRADO"
            rep.log(f"  {radicado}: no encontrado en el buscador.")
            rep.agregar(fila)
            return
        if not abrir_detalle(page, radicado):
            fila["resultado"] = "NO SE ABRIO DETALLE"
            rep.agregar(fila)
            return

        datos = leer_datos_detalle(page)
        fila.update({"tipo_tramite": datos["tipo_tramite"], "npn": datos["npn"]})

        # Validacion tecnica alfanumerica del NPN
        if datos["npn"]:
            ok_npn, det_npn = validar_npn(datos["npn"])
            fila["npn_longitud"] = len(datos["npn"])
            fila["npn_valido"] = "SI" if ok_npn else "NO"
            if not ok_npn:
                hallazgos.append(f"NPN: {det_npn}")
        else:
            fila["npn_valido"] = "SIN NPN"
            hallazgos.append("No se pudo leer el NPN del detalle")

        est = estado_validaciones(page)
        rep.log(f"  Tipo: {datos['tipo_tramite'] or '?'} | NPN: {datos['npn'] or '?'} "
                f"({fila['npn_longitud']}) | Val tecnica: {est['tecnica']} | "
                f"juridica: {est['juridica']}")

        capturar(page, f"{radicado}_detalle")

        # Validacion tecnica (si esta pendiente)
        if est["tecnica"] != "Aprobado":
            if aprobar_validacion(page, OBS_TECNICA, dry_run):
                rep.log(f"  Tecnica: {'(dry-run) ' if dry_run else ''}aprobada.")
            else:
                hallazgos.append("No se encontro boton de validacion tecnica")
        else:
            rep.log("  Tecnica ya estaba aprobada.")

        page.wait_for_timeout(1200)

        # Validacion juridica (si esta pendiente)
        est = estado_validaciones(page)
        if est["juridica"] != "Aprobado":
            if aprobar_validacion(page, OBS_JURIDICA, dry_run):
                rep.log(f"  Juridica: {'(dry-run) ' if dry_run else ''}aprobada.")
            else:
                hallazgos.append("No se encontro boton de validacion juridica")
        else:
            rep.log("  Juridica ya estaba aprobada.")

        capturar(page, f"{radicado}_final")
        fila["resultado"] = "OBSERVACION" if hallazgos else "OK"
    except PWTimeout as e:
        fila["resultado"] = "TIMEOUT"
        hallazgos.append(f"Timeout: {e}")
        capturar(page, f"{radicado}_error")
    except Exception as e:
        fila["resultado"] = "ERROR"
        hallazgos.append(f"{type(e).__name__}: {e}")
        capturar(page, f"{radicado}_error")

    fila["hallazgos"] = " | ".join(hallazgos)
    rep.agregar(fila)


def listar_asignados_pendientes(page, base_url: str, rep: Reporte) -> list[str]:
    """Recorre el listado de Asignado (usando el buscador vacio + paginacion best-effort)
    y devuelve los radicados cuya validacion este Pendiente. Como la paginacion puede
    fallar, se recomienda pasar la lista explicita de radicados."""
    ir_asignacion(page, base_url)
    # Filtrar estado Asignado
    try:
        page.get_by_text("Todos los estados", exact=False).first.click()
        page.wait_for_timeout(400)
        page.locator("label", has_text="Asignado").first.locator(
            "input[type=checkbox]").check()
        page.wait_for_timeout(400)
        page.keyboard.press("Escape")
        page.wait_for_load_state("networkidle")
    except Exception:
        pass
    pendientes = []
    filas = page.locator("table tbody tr")
    for i in range(filas.count()):
        t = filas.nth(i).inner_text()
        import re
        m = re.search(r"R-\d{4}-\d{4}", t)
        if m and "Pendiente" in t:
            pendientes.append(m.group(0))
    rep.log(f"Pendientes detectados (pagina actual): {', '.join(pendientes) or 'ninguno'}")
    rep.log("NOTA: la deteccion automatica solo cubre la pagina visible. Para lote "
            "completo, pasar la lista de radicados como argumentos.")
    return sorted(set(pendientes))


def main() -> None:
    parser = argparse.ArgumentParser(description="Validador QA en lote (tecnica+juridica)")
    parser.add_argument("radicados", nargs="*", help="radicados a validar (R-2026-XXXX)")
    parser.add_argument("--todos", action="store_true",
                        help="detecta y valida los Pendientes de la pagina actual")
    parser.add_argument("--dry-run", action="store_true",
                        help="no aprueba; solo abre/cierra el modal (prueba segura)")
    args = parser.parse_args()

    cfg = cargar_config()
    rep = Reporte()
    rep.log("Inicio del validador QA en lote.")
    if args.dry_run:
        rep.log("MODO DRY-RUN: no se aprobara ninguna validacion.")

    p, browser, page = conectar(cfg)
    try:
        radicados = list(args.radicados)
        if args.todos and not radicados:
            radicados = listar_asignados_pendientes(page, cfg["url"], rep)
        if not radicados:
            rep.log("No hay radicados para procesar. Pasa radicados o usa --todos.")
            return
        rep.log(f"Radicados a procesar ({len(radicados)}): {', '.join(radicados)}")
        for r in radicados:
            procesar_radicado(page, cfg["url"], r, rep, args.dry_run)
    finally:
        rep.cerrar()
        try:
            p.stop()
        except Exception:
            pass
        rep.log("Fin. El navegador sigue abierto.")


if __name__ == "__main__":
    main()
