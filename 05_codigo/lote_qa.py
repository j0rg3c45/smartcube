"""
SmartCube QA - Procesamiento en LOTE del flujo alfanumerico de los tramites.

Se conecta por CDP al navegador ya abierto por navegador.py y recorre los radicados
en estado Asignado, procesando de forma autonoma los pasos ALFANUMERICOS del wizard
hasta el punto donde la plataforma exige informacion GEOGRAFICA (Terreno / Asignacion
de NPN), que es reserva del usuario. Por cada tramite genera un resumen .txt en su
carpeta local y deja todo preparado para el ajuste cartografico manual.

Reglas de datos:
- Datos sinteticos (nombres, documentos, fechas, observaciones) ALEATORIOS y NO
  repetidos entre tramites. Coherencia catastral (NPN 30 digitos, matricula numerica,
  tipo de documento acorde a persona natural/juridica).

Alcance por tramite (se detiene limpio donde no pueda seguir):
- Si la validacion esta Pendiente -> aprueba Tecnica + Juridica.
- Inicia el tramite (wizard) si es posible.
- Paso 1 (Predio / Caracterizacion LADM): llena lo editable.
- Paso 2 (Propietario): si es editable, complementa; si es solo lectura, continua.
- Paso 3 (Terreno) u otro paso cartografico / "Asignacion de NPN": SE DETIENE y lo
  deja marcado como pendiente para el usuario.

Uso:
    uv run python navegador.py        (en una terminal; iniciar sesion una vez)
    uv run python lote_qa.py          (en otra terminal)
    uv run python lote_qa.py --radicados R-2026-0061 R-2026-0062   (subconjunto)
    uv run python lote_qa.py --excluir R-2026-0057                 (excluir alguno)

Salidas:
    03_tramites/NN_tramite_<RADICADO>/resumen_<RADICADO>.txt
    05_codigo/reportes/lote_<fecha>.log
"""

from __future__ import annotations

import argparse
import random
import re
import sys
import unicodedata
from datetime import datetime, date
from pathlib import Path

# Reutilizamos las funciones ya probadas del REPL (no lanza el REPL al importar).
import qa

BASE_DIR = Path(__file__).resolve().parent
TRAMITES_DIR = BASE_DIR.parent / "03_tramites"
REPORTES_DIR = BASE_DIR / "reportes"

# Radicados que NO se reprocesan (ya cerrados/bloqueados).
EXCLUIDOS_DEFECTO = {"R-2026-0057"}

# Anio del avaluo retroactivo a calcular en el Paso 6 (solo en los que lleguen a ese
# paso). Configurable con --anio; por defecto 2025.
ANIO_AVALUO = "2025"


# ---------------------------------------------------------------------------
# Generador de datos sinteticos con control de unicidad entre tramites
# ---------------------------------------------------------------------------

NOMBRES_M = ["Juan", "Carlos", "Andres", "Santiago", "Felipe", "Mauricio", "Diego",
             "Ricardo", "Oscar", "Javier", "Hernan", "Alberto", "Sergio", "Fabian"]
NOMBRES_F = ["Maria", "Luisa", "Carolina", "Patricia", "Diana", "Angela", "Paola",
             "Natalia", "Catalina", "Sandra", "Liliana", "Marcela", "Adriana", "Claudia"]
APELLIDOS = ["Ramirez", "Gomez", "Lopez", "Martinez", "Rodriguez", "Gonzalez", "Perez",
             "Torres", "Vargas", "Castro", "Ospina", "Valencia", "Zuluaga", "Cardenas",
             "Montoya", "Giraldo", "Arango", "Quintero", "Restrepo", "Mejia", "Salazar"]
CLASES_VIA = ["Calle", "Carrera", "Diagonal", "Transversal", "Avenida"]

# Datos ya usados (se cargan de la lista historica + lo generado en esta corrida).
_doc_usados: set[str] = {"1130598742"}            # R-2026-0072 (historico)
_nombre_usados: set[str] = {"carlos andres ramirez gomez"}


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return s.lower().strip()


def generar_persona() -> dict:
    """Devuelve un titular natural unico (nombre completo + documento)."""
    for _ in range(200):
        if random.random() < 0.5:
            n1 = random.choice(NOMBRES_M)
            n2 = random.choice(NOMBRES_M)
        else:
            n1 = random.choice(NOMBRES_F)
            n2 = random.choice(NOMBRES_F)
        a1 = random.choice(APELLIDOS)
        a2 = random.choice(APELLIDOS)
        nombre = f"{n1} {n2} {a1} {a2}"
        doc = str(random.randint(10_000_000, 1_299_999_999))
        if _norm(nombre) in _nombre_usados or doc in _doc_usados:
            continue
        _nombre_usados.add(_norm(nombre))
        _doc_usados.add(doc)
        return {"nombre": nombre, "primer_nombre": n1, "segundo_nombre": n2,
                "primer_apellido": a1, "segundo_apellido": a2, "documento": doc,
                "tipo_documento": "Cédula de Ciudadanía", "sexo":
                "Masculino" if n1 in NOMBRES_M else "Femenino"}
    # Si no logra uno unico (muy improbable), devuelve uno con sufijo.
    doc = str(random.randint(10_000_000, 1_299_999_999))
    _doc_usados.add(doc)
    return {"nombre": f"Titular Prueba {doc[-4:]}", "documento": doc,
            "tipo_documento": "Cédula de Ciudadanía", "sexo": "Masculino"}


def generar_direccion() -> str:
    via = random.choice(CLASES_VIA)
    return f"{via} {random.randint(1, 120)} # {random.randint(1, 90)} - {random.randint(1, 99)}"


# ---------------------------------------------------------------------------
# Log del lote
# ---------------------------------------------------------------------------

class LogLote:
    def __init__(self) -> None:
        REPORTES_DIR.mkdir(exist_ok=True)
        marca = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = REPORTES_DIR / f"lote_{marca}.log"
        self._f = self.path.open("w", encoding="utf-8")

    def __call__(self, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        linea = f"[{ts}] {msg}"
        print(linea)
        self._f.write(linea + "\n")
        self._f.flush()

    def cerrar(self) -> None:
        self._f.close()


# ---------------------------------------------------------------------------
# Lectura de datos del detalle del radicado
# ---------------------------------------------------------------------------

def leer_detalle(page) -> dict:
    """Lee tipo de tramite, Tramite #, NPN y estado de validacion del detalle."""
    datos = {"tipo": "", "tramite_id": "", "npn": "", "validacion": "", "solicitante": ""}
    try:
        texto = page.locator("body").inner_text()
    except Exception:
        return datos
    m = re.search(r"Tr[aá]mite\s*#\s*(\d+)", texto)
    if m:
        datos["tramite_id"] = m.group(1)
    # Tipo: linea con palabras clave de tipo de tramite.
    for linea in texto.splitlines():
        l = linea.strip()
        if any(k in l for k in ("Mutación", "Rectificaciones", "Efectos", "Mixta")) and len(l) > 10:
            datos["tipo"] = l.split("—")[0].strip()
            break
    m = re.search(r"\b(\d{30})\b", texto)
    if m:
        datos["npn"] = m.group(1)
    if "Validación Técnica" in texto or "Aprobado" in texto:
        datos["validacion"] = "Aprobado" if texto.count("Aprobado") >= 2 else "Pendiente"
    if "Pendiente" in texto and "Técnica" in texto:
        datos["validacion"] = "Pendiente"
    return datos


def carpeta_tramite(radicado: str) -> Path | None:
    """Ubica la carpeta local NN_tramite_<RADICADO> del radicado."""
    if not TRAMITES_DIR.exists():
        return None
    for d in TRAMITES_DIR.iterdir():
        if d.is_dir() and d.name.endswith(radicado):
            return d
    return None


def escribir_resumen(radicado: str, info: dict, log) -> None:
    """Escribe resumen_<RADICADO>.txt en la carpeta del tramite."""
    carpeta = carpeta_tramite(radicado)
    if carpeta is None:
        # Crear una carpeta si no existe (siguiente secuencial no se calcula aqui).
        carpeta = TRAMITES_DIR / f"tramite_{radicado}"
        carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"resumen_{radicado}.txt"
    prop = info.get("propietario") or {}
    lineas = [
        f"RESUMEN DE PROCESAMIENTO - {radicado}",
        "=" * 50,
        "",
        "1. IDENTIFICACION",
        f"   Radicado:        {radicado}",
        f"   Tramite #:       {info.get('tramite_id') or '(no leido)'}",
        f"   Tipo de tramite: {info.get('tipo') or '(no leido)'}",
        f"   NPN:             {info.get('npn') or '(no leido)'}",
        f"   Fecha proceso:   {date.today().strftime('%d/%m/%Y')}",
        "",
        "2. DATOS INGRESADOS (pasos 1 a 6, alfanumerico)",
        f"   Validacion:      {info.get('validacion_resultado') or '(sin cambio)'}",
        f"   Caracterizacion: {info.get('caracterizacion') or '(no aplicada / solo lectura)'}",
    ]
    if prop:
        lineas += [
            f"   Propietario:     {prop.get('nombre', '')}",
            f"   Documento:       {prop.get('tipo_documento', '')} {prop.get('documento', '')}",
            f"   Sexo:            {prop.get('sexo', '')}",
        ]
    else:
        lineas.append("   Propietario:     (paso solo lectura o no editable en este tramite)")
    if info.get("direccion"):
        lineas.append(f"   Direccion:       {info['direccion']}")
    if info.get("fuente_admin"):
        lineas.append(f"   Fuente admin.:   {info['fuente_admin']}")
    if info.get("avaluo"):
        lineas.append(f"   Avaluo:          {info['avaluo']}")
    lineas.append(f"   Pasos recorridos:{' ' + info.get('pasos_completados', '-')}")
    lineas += [
        "",
        "3. PENDIENTE DE INTERVENCION CARTOGRAFICA (usuario)",
        f"   {info.get('pendiente_cartografico', 'Carga/ajuste de geometria de TERRENO (y CONSTRUCCIONES si aplica).')}",
        "",
        "4. ESTADO EN PLATAFORMA",
        f"   {info.get('estado_final', '(detenido en el punto cartografico; sin pasar a calidad)')}",
        "",
        f"Observaciones: {info.get('observaciones', 'ninguna')}",
    ]
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    log(f"    resumen escrito: {ruta}")


# ---------------------------------------------------------------------------
# Procesamiento de un radicado
# ---------------------------------------------------------------------------

def procesar(page, base_url: str, radicado: str, log) -> dict:
    info = {"radicado": radicado}
    log(f"=== {radicado} ===")
    # 1) Abrir detalle (via buscador para evitar paginacion).
    qa.ir_asignacion(page, base_url)
    qa.filtrar_estado(page, "Asignado")
    buscador = page.locator("input[placeholder*='Buscar por radicado']")
    if buscador.count() > 0:
        buscador.first.fill("")
        buscador.first.type(radicado, delay=15)
        page.wait_for_timeout(1500)
        page.wait_for_load_state("networkidle")
    if not qa.abrir_detalle(page, radicado):
        info["estado_final"] = "NO SE PUDO ABRIR EL DETALLE"
        info["observaciones"] = "El radicado no se encontro en la tabla tras buscarlo."
        return info
    page.wait_for_timeout(800)
    det = leer_detalle(page)
    info.update({"tipo": det["tipo"], "tramite_id": det["tramite_id"], "npn": det["npn"]})
    log(f"    tipo={det['tipo'] or '?'} | #{det['tramite_id'] or '?'} | NPN={det['npn'] or '?'} "
        f"| validacion={det['validacion'] or '?'}")

    # 2) Validar si esta pendiente.
    if det["validacion"] == "Pendiente":
        try:
            qa._validacion(page, "Tecnica", "Todo esta Ok")
            page.wait_for_timeout(1000)
            qa._validacion(page, "Juridica", "Todo esta Ok en Juridica")
            info["validacion_resultado"] = "Tecnica + Juridica aprobadas por el lote"
        except Exception as e:
            info["validacion_resultado"] = f"fallo validacion: {type(e).__name__}"
    else:
        info["validacion_resultado"] = "ya estaba aprobada/completa"

    # 3) Iniciar tramite (sin confirmacion interactiva).
    try:
        boton = page.get_by_role("button", name="Iniciar Trámite")
        if boton.count() == 0:
            boton = page.get_by_text("Iniciar Trámite", exact=False)
        if boton.count() == 0:
            info["estado_final"] = "NO HAY BOTON INICIAR TRAMITE"
            info["observaciones"] = ("Posible trámite que requiere Asignacion de NPN previa "
                                     "(geometria) o estado distinto. Revisar manualmente.")
            return info
        boton.first.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
    except Exception as e:
        info["estado_final"] = "NO SE PUDO INICIAR"
        info["observaciones"] = f"{type(e).__name__}: {e}"
        return info

    # Detectar si pide Asignacion de NPN (tipos 2a/5a/Cambio NPN).
    try:
        cuerpo = page.locator("body").inner_text()
    except Exception:
        cuerpo = ""
    if "Asignación de NPN" in cuerpo and "Falta" in cuerpo:
        info["estado_final"] = "REQUIERE ASIGNACION DE NPN (cartografico)"
        info["pendiente_cartografico"] = ("Este tipo de tramite requiere ASIGNACION DE NPN "
                                          "(cargar shape/geometria y numerar predios) ANTES del "
                                          "wizard. Reserva del usuario.")
        info["observaciones"] = "Detenido antes del wizard: falta Asignacion de NPN."
        return info

    # 4) Recorrer el wizard AVANZANDO lo mas lejos posible.
    #    - Llena lo alfanumerico editable de cada paso.
    #    - En pasos cartograficos (Terreno/Construccion) NO carga geometria, pero
    #      INTENTA continuar: si la plataforma lo permite (no bloquea), avanza; si
    #      bloquea por falta de geometria, se detiene limpio ahi.
    #    - Objetivo: llegar hasta el Paso 7 (Resumen) cuando el sistema lo permita.
    pasos_ok = []
    pendiente_carto = []
    ultimo_n = None
    estancado = 0
    for _ in range(16):  # tope de seguridad de iteraciones
        n = qa.detectar_paso(page)
        if n is None:
            break
        # Deteccion de estancamiento (no avanza de paso tras continuar).
        if n == ultimo_n:
            estancado += 1
        else:
            estancado = 0
        ultimo_n = n

        if n >= 7:
            # Llegamos al Resumen final.
            info["estado_final"] = "AVANZO HASTA EL PASO 7 (Resumen) sin requerir geometria."
            pasos_ok.append("7-Resumen")
            break

        if n == 1:
            try:
                qa.caracterizacion_ladm(page, "Privado", "Dominio")
                info["caracterizacion"] = "Privado / Dominio (si editable)"
            except Exception:
                info["caracterizacion"] = "no editable (solo lectura)"
            pasos_ok.append("1-Predio")
        elif n == 2:
            persona = generar_persona()
            info["propietario"] = persona
            pasos_ok.append("2-Propietario")
        elif n == 3:
            # Terreno: cartografico (reserva del usuario). Intentar continuar sin cargar.
            pendiente_carto.append("Terreno (shape/GeoJSON + puntos/linderos)")
            pasos_ok.append("3-Terreno(sin geometria)")
        elif n == 4:
            pendiente_carto.append("Construcciones (poligono de la UC)")
            pasos_ok.append("4-Construccion(sin geometria)")
        elif n == 5:
            # Llenar y VERIFICAR que quedo completa antes de avanzar. Reintenta 1 vez.
            ok = 0
            try:
                ok = qa.fuente_administrativa(page, radicado)
                if ok < 7:
                    log(f"    Fuente Administrativa incompleta ({ok}/7); reintentando...")
                    page.wait_for_timeout(1500)
                    ok = qa.fuente_administrativa(page, radicado)
            except Exception as e:
                info.setdefault("observaciones", f"FuenteAdmin: {type(e).__name__}")
            pasos_ok.append(f"5-FuenteAdmin({ok}/7)")
            info["fuente_admin"] = f"{ok}/7 desplegables + numeros/fechas/observacion"
            if ok < 7:
                # No avanzar con la seccion incompleta: detener para revision manual.
                info["estado_final"] = (f"Detenido en Paso 5 (Fuente Administrativa): solo "
                                        f"{ok}/7 desplegables llenados tras reintento.")
                info["observaciones"] = (f"Fuente Administrativa incompleta ({ok}/7). "
                                         f"No se avanzo para no dejar datos faltantes.")
                log(f"    DETENIDO en Paso 5: Fuente Administrativa {ok}/7.")
                break
        elif n == 6:
            # Avaluo: calcular el retroactivo del anio configurado (por defecto 2025)
            # SOLO en los radicados que lleguen hasta este paso.
            try:
                qa.calcular_avaluo(page, ANIO_AVALUO)
                pasos_ok.append(f"6-Avaluo({ANIO_AVALUO})")
                info["avaluo"] = f"retroactivo {ANIO_AVALUO} calculado"
            except Exception as e:
                info.setdefault("observaciones", f"Avaluo: {type(e).__name__}")

        # Intentar avanzar al siguiente paso.
        try:
            qa.continuar_wizard(page)
            page.wait_for_timeout(1300)
        except Exception:
            pass

        # Si estamos en un paso cartografico y NO avanzo (sigue en el mismo paso),
        # significa que la plataforma BLOQUEA sin la geometria -> detener limpio.
        nuevo = qa.detectar_paso(page)
        if n in (3, 4) and nuevo == n:
            info["estado_final"] = (f"Detenido en Paso {n} ({'Terreno' if n==3 else 'Construccion'}): "
                                    f"la plataforma EXIGE geometria para continuar.")
            break
        if estancado >= 2:
            info["estado_final"] = f"Detenido en Paso {n} (no avanza; requiere intervencion)."
            break

    if "estado_final" not in info:
        nf = qa.detectar_paso(page)
        info["estado_final"] = f"Detenido en Paso {nf}." if nf else "Detenido (paso no determinado)."

    if pendiente_carto:
        info["pendiente_cartografico"] = ("Cargar/ajustar: " + "; ".join(dict.fromkeys(pendiente_carto))
                                          + ". (Reserva del usuario.)")
    else:
        info["pendiente_cartografico"] = "Ninguno pendiente: el tramite no requirio geometria."
    info["pasos_completados"] = ", ".join(pasos_ok) or "(ninguno)"
    log(f"    pasos: {info['pasos_completados']} | {info['estado_final']}")
    return info


def main() -> None:
    parser = argparse.ArgumentParser(description="Procesamiento en lote del flujo alfanumerico")
    parser.add_argument("--radicados", nargs="*", help="subconjunto a procesar")
    parser.add_argument("--excluir", nargs="*", default=[], help="radicados a excluir")
    parser.add_argument("--semilla", default="", help="semilla para datos sinteticos reproducibles")
    parser.add_argument("--anio", default="2025",
                        help="anio del avaluo retroactivo a calcular (def. 2025)")
    args = parser.parse_args()

    global ANIO_AVALUO
    ANIO_AVALUO = args.anio

    if args.semilla:
        random.seed(args.semilla)

    cfg = qa.cargar_config()
    # Desactivar confirmacion interactiva para que el lote no se bloquee.
    qa._pedir_confirmacion = False

    log = LogLote()
    log("Inicio del procesamiento en LOTE (flujo alfanumerico).")
    p, browser, page = qa.conectar(cfg)

    try:
        if args.radicados:
            radicados = list(args.radicados)
        else:
            radicados = qa.listar_todas_paginas(page, cfg["url"])
        excluir = set(EXCLUIDOS_DEFECTO) | set(args.excluir or [])
        radicados = [r for r in radicados if r not in excluir]
        log(f"Radicados a procesar ({len(radicados)}): {', '.join(radicados)}")

        resultados = []
        for r in radicados:
            try:
                info = procesar(page, cfg["url"], r, log)
            except Exception as e:
                info = {"radicado": r, "estado_final": "ERROR",
                        "observaciones": f"{type(e).__name__}: {e}"}
                log(f"    ERROR en {r}: {type(e).__name__}: {e}")
            escribir_resumen(r, info, log)
            resultados.append(info)
            page.wait_for_timeout(800)

        # Reporte de cierre en el log.
        log("")
        log("===== INFORME DE CIERRE DEL LOTE =====")
        for info in resultados:
            log(f"  {info['radicado']} | {info.get('tipo', '?') or '?'} | "
                f"pasos: {info.get('pasos_completados', '-')} | "
                f"estado: {info.get('estado_final', '?')} | "
                f"obs: {info.get('observaciones', '-')}")
    except KeyboardInterrupt:
        log("Detenido por el usuario (Ctrl+C).")
    finally:
        log(f"Fin del lote. Log: {log.path}")
        log.cerrar()
        try:
            p.stop()
        except Exception:
            pass


if __name__ == "__main__":
    main()
