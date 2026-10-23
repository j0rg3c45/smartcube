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
    entrar <R-...>        AUTO COMPLETO: busca, abre detalle y pulsa 'Iniciar
                          Tramite' -> entra directo al wizard (para revisar)
    siguiente             AUTO: abre el radicado MENOR en estado Asignado
    iniciar               pulsa 'Iniciar Tramite' (ACCION CRITICA)
    listar                recorre TODAS las paginas y lista los Asignado ordenados
    validar <R-...>       AUTO: abre detalle y aprueba validacion tecnica + juridica

  Wizard "Gestion de Tramites" (parte tecnica):
    paso                  diagnostica el paso actual: si es automatizable (el
                          agente lo llena) o manual (el usuario debe actuar)
    puntosmasivo <TP>|<Metodo>|<PC>
                          Paso 3: llena en bloque TODA la tabla de Puntos
                          (Tipo de punto / Metodo / Punto de control) de corrido.
                          Ej: puntosmasivo Mojón | Método Directo | Apoyo
    linderosmasivo <ruta.geojson>
                          Paso 3 (pestaña Linderos): llena en bloque los 55 linderos.
                          La ORIENTACION se calcula REAL desde el poligono (azimut de
                          cada segmento); 'Colinda con' y NPN/nombre son sinteticos
                          coherentes. Ej: linderosmasivo C:\\...\\predio.geojson
    fuenteadmin [semilla] Paso 5: rellena TODA la Fuente Administrativa con datos
                          sinteticos (tipo fuente, adquisicion, ente, depto/muni,
                          numeros y fechas). La semilla (p.ej. el radicado) fija la
                          aleatoriedad. Ej: fuenteadmin R-2026-0057
    avaluo <anio>         Paso 6: elige la vigencia del retroactivo y pulsa 'Calcular
                          retroactivo' automaticamente. Ej: avaluo 2025
    caracterizacion [TP]|[TD]
                          Paso 1: llena la Caracterizacion LADM (Tipo de Predio /
                          Tipo de Derecho). Def: Privado | Dominio.
                          Ej: caracterizacion Privado | Dominio
    editardireccion [semilla]
                          Paso 1: edita la direccion del predio dejandola ESTRUCTURADA
                          (LADM) y la llena con datos sinteticos (clase de via, valores,
                          numero, codigo postal) + Actualizar. Ej: editardireccion R-2026-0061
    destino [valor]       Paso 1: cambia el Destino Económico (def. Habitacional). Usar
                          en tramites CON construccion para no dejar destino de lote.
                          Ej: destino Habitacional | destino Comercial
    construccion [anio] [semilla]
                          Paso 4: llena el modal 'Nueva unidad de construccion' con
                          datos sinteticos de vivienda (tipo Residencial, uso, año,
                          estado Bueno, baños/habs, y la CALIFICACION CATASTRAL completa
                          - 16 desplegables). Requiere geometria ya cargada. Luego
                          revisar y pulsar 'Agregar UC'. Ej: construccion 2010 R-2026-0061
    propietario [semilla] [modo] [n]
                          Paso 2 (Cambio de Propietario). Datos sinteticos UNICOS,
                          Persona Natural, etnico=Ninguno (OBLIGATORIO), Dominio.
                          modo=sustitucion (def): ELIMINA titular(es) previo(s) y
                            registra 1 nuevo al 100%.
                          modo=copropiedad: NO elimina; agrega n copropietarios
                            repartiendo 100% en partes iguales.
                          Ej: propietario R-2026-0081            (sustitucion 100%)
                          Ej: propietario R-2026-0082 copropiedad 2  (2 al 50%)
    tramite3a [semilla] [destino]
                          Mutacion 3a de CORRIDO hasta el Resumen: Paso 1 (direccion solo
                          si NO estructurada; destino solo si se indica) -> Terreno y
                          Construccion se AVANZAN (sin cargar geometria ni editar UC) ->
                          Fuente Admin + Avaluo + Resumen validando. El usuario AJUSTA la
                          construccion al final (cargar geometria + calificacion) y
                          re-valida. NO pasa a calidad. Ej: tramite3a R-2026-0088
    tramite3afin [semilla] [anio]
                          Mutacion 3a: tras AJUSTAR la construccion (geometria + edicion
                          de calificacion), edita la UC y avanza Fuente Admin + Avaluo +
                          Resumen validando. (Usar si se proceso la construccion aparte.)
    autopaso [semilla]    AUTO-ADAPTATIVO: inspecciona el paso actual, llena los campos
                          EDITABLES (input/select/textarea) con datos sinteticos y
                          registra los bloqueados (disabled/readonly). No toca geometria.
    tramiteauto [semilla] [anio]
                          Motor AUTO-ADAPTATIVO: recorre el wizard de corrido hasta el
                          Resumen aplicando autopaso en cada paso + avaluo (año def 2025).
                          Geometria = reserva del usuario; NO pasa a calidad. Sirve para
                          tipos nuevos/atipicos. Ej: tramiteauto R-2026-0062 2025
    cancelacion [semilla] Tramite 'Cancelaciones - Fuerza Mayor' (3 pasos): llena el
                          Motivo de la cancelacion (causa de fuerza mayor variada) y la
                          Fuente Administrativa, avanza al Resumen y valida. NO pasa a
                          calidad. Ej: cancelacion R-2026-0086
    tramitepropietario [semilla] [modo] [n]
                          Proceso COMPLETO de Cambio de Propietario (estando en Paso 2):
                          hace el cambio y AVANZA hasta el Resumen validando. NO pasa a
                          calidad (critico, lo confirma el usuario). Ej: tramitepropietario R-2026-0081
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

# Direcciones estructuradas ya usadas (firma vp/vg/num) para NO repetir entre tramites.
_direcciones_usadas: set = set()


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


def _validacion(page, nombre: str, observacion: str) -> bool:
    """Ejecuta UNA validacion (tecnica o juridica) desde el detalle del radicado.

    Pulsa 'Realizar Validacion', escribe la observacion, deja Resultado APROBADO
    y pulsa 'Aprobar'. Devuelve True si la ejecuto.
    """
    boton = page.get_by_role("button", name="Realizar Validación")
    if boton.count() == 0:
        print(f"  No hay boton 'Realizar Validacion' para {nombre} (quiza ya validada).")
        return False
    boton.first.click()
    page.wait_for_timeout(700)
    # Observaciones (textarea del modal).
    ta = page.locator("textarea[placeholder='Observaciones opcionales...']")
    if ta.count() == 0:
        ta = page.locator("textarea")
    if ta.count() > 0:
        ta.first.fill(observacion)
    # Resultado ya viene en APROBADO por defecto. Pulsar Aprobar.
    aprobar = page.get_by_role("button", name="Aprobar")
    if aprobar.count() == 0:
        aprobar = page.locator("button", has_text="Aprobar")
    aprobar.first.click()
    page.wait_for_timeout(1500)
    page.wait_for_load_state("networkidle")
    print(f"  Validacion {nombre} APROBADA (obs: {observacion!r}).")
    return True


def validar_radicado(page, base_url: str, radicado: str) -> None:
    """Emula el proceso de validacion completo de un radicado: abre su detalle y
    aprueba la validacion tecnica y la juridica, de corrido."""
    print(f"  [1/3] Abriendo detalle de {radicado}...")
    if not abrir_radicado(page, base_url, radicado):
        return
    page.wait_for_timeout(800)
    print("  [2/3] Validacion Tecnica...")
    _validacion(page, "Tecnica", "Todo esta Ok")
    page.wait_for_timeout(1200)
    print("  [3/3] Validacion Juridica...")
    _validacion(page, "Juridica", "Todo esta Ok en Juridica")
    print("  Validaciones completadas. Revisa el detalle y usa 'iniciar' para el wizard.")
    mostrar_estado(page)


def listar_todas_paginas(page, base_url: str) -> list[str]:
    """Recorre TODAS las paginas del listado de Asignacion (filtrado) y junta los
    radicados de todas, ordenados de menor a mayor."""
    ir_asignacion(page, base_url)
    filtrar_estado(page, "Asignado")
    todos = []
    pagina = 1
    while True:
        page.wait_for_timeout(500)
        rads = listar_radicados(page)
        for r in rads:
            if r not in todos:
                todos.append(r)
        print(f"  Pagina {pagina}: {', '.join(rads)}")
        # Intentar ir a la pagina siguiente.
        sig = page.get_by_role("button", name="Siguiente")
        if sig.count() == 0:
            sig = page.locator("button", has_text="Siguiente")
        if sig.count() == 0 or sig.first.is_disabled():
            break
        # Guardar el conjunto actual para detectar cuando cambie la pagina.
        set_antes = set(rads)
        try:
            sig.first.click()
            pagina += 1
            page.wait_for_load_state("networkidle")
            # Esperar hasta 5s a que la tabla cambie (conjunto distinto al anterior).
            for _ in range(10):
                page.wait_for_timeout(500)
                nuevos = set(listar_radicados(page))
                if nuevos and nuevos != set_antes:
                    break
        except Exception:
            break
    todos_ordenados = sorted(todos)
    print(f"\n  TOTAL radicados Asignado ({len(todos_ordenados)}): {', '.join(todos_ordenados)}")
    if todos_ordenados:
        print(f"  MENOR: {todos_ordenados[0]}")
    return todos_ordenados


# --- Diagnostico de paso del wizard (que es automatizable y que es manual) ---

# Mapa de los 8 pasos del wizard. Para cada paso: nombre, naturaleza y accion.
#   naturaleza: 'auto'   = el agente lo rellena/avanza (alfanumerico o solo lectura)
#               'manual' = requiere intervencion del usuario (cartografico GIS)
WIZARD_PASOS = {
    1: {"nombre": "PREDIO",
        "naturaleza": "auto",
        "detalle": "Datos del predio (codificacion NPN, matricula, destino, "
                   "caracterizacion LADM). Suele ser solo lectura. Opcional: foto "
                   "del predio (la sube el USUARIO manualmente)."},
    2: {"nombre": "PROPIETARIO",
        "naturaleza": "auto",
        "detalle": "Propietarios del predio. En Efectos Registrales es SOLO LECTURA "
                   "(no editable). En Rectificaciones es EDITABLE (complementar datos "
                   "faltantes y % participacion con datos sinteticos)."},
    3: {"nombre": "TERRENO",
        "naturaleza": "manual",
        "detalle": "CARTOGRAFICO. Geometria del terreno (shape/GeoJSON), puntos y "
                   "linderos. Lo gestiona el USUARIO en el visor SIG: subir/conservar "
                   "shape, describir linderos (orientacion, colinda con, NPN) y Guardar."},
    4: {"nombre": "CONSTRUCCION",
        "naturaleza": "manual",
        "detalle": "CARTOGRAFICO/MIXTO. Unidades de construccion y su poligono (altura). "
                   "Preguntar al usuario si el predio tiene construccion. Si tiene, el "
                   "USUARIO carga el poligono; los datos alfanumericos de la UC (area, "
                   "calificacion, anio, avaluo) los puede completar el agente."},
    5: {"nombre": "FUENTE ADMINISTRATIVA",
        "naturaleza": "auto",
        "detalle": "Formulario alfanumerico (fuente administrativa del acto). Lo rellena "
                   "el agente con datos sinteticos."},
    6: {"nombre": "AVALUO",
        "naturaleza": "auto",
        "detalle": "Calculo de avaluo retroactivo. El agente PREGUNTA al usuario desde "
                   "que anio recalcular y luego ejecuta el calculo."},
    7: {"nombre": "RESUMEN",
        "naturaleza": "auto",
        "detalle": "Validaciones finales (topologia, reglas de negocio). Deben quedar en "
                   "0 errores. Si hay errores, se corrigen y se re-valida."},
    8: {"nombre": "BORRADOR RESOLUCION",
        "naturaleza": "auto",
        "detalle": "Editor del borrador + vista previa PDF. Luego 'Pasar a calidad'."},
}


def detectar_paso(page) -> int | None:
    """Detecta el numero de paso activo del wizard (1..8) leyendo el stepper.

    El paso activo tiene su etiqueta con clase 'text-primary'. Devuelve el numero
    o None si no se puede determinar.
    """
    import re
    # Buscar etiquetas del tipo "N. NOMBRE" marcadas como activas (text-primary).
    try:
        activos = page.locator("span.text-primary")
        for i in range(activos.count()):
            t = activos.nth(i).inner_text().strip()
            m = re.match(r"\s*(\d)\.\s", t)
            if m:
                return int(m.group(1))
    except Exception:
        pass
    # Respaldo: buscar el encabezado "N. NOMBRE" visible como titulo del paso.
    try:
        cuerpo = page.locator("body").inner_text()
        for n, info in WIZARD_PASOS.items():
            if re.search(rf"\b{n}\.\s*{info['nombre'].split()[0]}", cuerpo, re.I):
                # No es determinista por si varios aparecen; se deja como ultimo recurso.
                pass
    except Exception:
        pass
    return None


def puntos_masivo(page, tipo_punto: str, metodo: str, punto_control: str) -> None:
    """Llena en bloque la tabla de Puntos del Paso 3 (Terreno).

    La tabla tiene, por cada punto, 3 <select> consecutivos en la pagina:
      posicion %3==0 -> Tipo de punto (p. ej. 'Mojon')
      posicion %3==1 -> Metodo        (p. ej. 'Metodo Directo')
      posicion %3==2 -> Punto de control (p. ej. 'Apoyo')
    Recorre TODOS los <select> y aplica el valor que corresponde a su columna,
    saltando los que ya tengan un valor distinto de vacio (no sobrescribe).
    """
    selects = page.locator("select")
    total = selects.count()
    if total == 0:
        print("  No hay desplegables en la pagina. ¿Estas en el Paso 3 (Puntos)?")
        return
    if total % 3 != 0:
        print(f"  AVISO: {total} desplegables no es multiplo de 3; se asume patron "
              f"Tipo/Metodo/Control de todas formas.")
    valores = {0: tipo_punto, 1: metodo, 2: punto_control}
    filas = total // 3
    print(f"  Llenando {filas} filas de Puntos ({total} desplegables) de corrido...")
    print(f"    Tipo de punto   = {tipo_punto!r}")
    print(f"    Metodo          = {metodo!r}")
    print(f"    Punto de control= {punto_control!r}")
    hechos = 0
    saltados = 0
    errores = 0
    for i in range(total):
        col = i % 3
        valor = valores[col]
        sel = selects.nth(i)
        try:
            # No sobrescribir si ya tiene un valor elegido.
            actual = sel.input_value()
            if actual not in ("", None):
                saltados += 1
                continue
            sel.select_option(label=valor)
            hechos += 1
            # Pausa breve cada cierto numero para no saturar la SPA.
            if i % 15 == 0:
                page.wait_for_timeout(120)
        except Exception as e:
            errores += 1
            if errores <= 5:
                print(f"    [fila ~{i//3 + 1}, col {col}] no se pudo: {type(e).__name__}")
    print(f"  Listo. Aplicados: {hechos} | ya tenian valor: {saltados} | errores: {errores}")
    print("  Revisa el aviso de filas por describir; usa 'cap' para confirmar.")


def _orientaciones_desde_geojson(ruta: str) -> list[str]:
    """Calcula la orientacion cardinal (Norte/Sur/Este/Oeste) de cada lindero del
    poligono, a partir del azimut del segmento entre vertices consecutivos.

    Da coherencia geografica: la orientacion de cada lado es la real del terreno.
    Devuelve [] si no puede leer el archivo.
    """
    import json
    import math
    archivo = Path(ruta.strip().strip('"'))
    if not archivo.exists():
        print(f"  No existe el GeoJSON: {archivo}")
        return []
    try:
        data = json.loads(archivo.read_text(encoding="utf-8"))
        geom = data["features"][0]["geometry"]
        # Soporta Polygon y MultiPolygon: tomar el primer anillo exterior.
        if geom["type"] == "MultiPolygon":
            coords = geom["coordinates"][0][0]
        else:
            coords = geom["coordinates"][0]
    except Exception as e:
        print(f"  No se pudo leer la geometria: {type(e).__name__}: {e}")
        return []

    def azimut(lon1, lat1, lon2, lat2):
        latm = math.radians((lat1 + lat2) / 2)
        dx = (lon2 - lon1) * math.cos(latm)
        dy = (lat2 - lat1)
        return (math.degrees(math.atan2(dx, dy)) + 360) % 360

    def cardinal(az):
        if az >= 315 or az < 45:
            return "Norte"
        if az < 135:
            return "Este"
        if az < 225:
            return "Sur"
        return "Oeste"

    orient = []
    n = len(coords) - 1  # el ultimo vertice repite el primero
    for i in range(n):
        lon1, lat1 = coords[i][0], coords[i][1]
        lon2, lat2 = coords[i + 1][0], coords[i + 1][1]
        orient.append(cardinal(azimut(lon1, lat1, lon2, lat2)))
    return orient


def linderos_masivo(page, ruta_geojson: str) -> None:
    """Llena en bloque la tabla de Linderos del Paso 3.

    Por cada lindero hay 2 <select> consecutivos en la pagina:
      posicion %2==0 -> Orientacion (Norte/Sur/Este/Oeste) -> se usa la REAL del
                        poligono (azimut del segmento).
      posicion %2==1 -> Colinda con (Predio/Via/Rio/Zona comun/Otro) -> aleatorio
                        coherente rural (mayoria Predio).
    Ademas rellena el campo de texto 'NPN o nombre del colindante' de cada fila con
    un valor sintetico coherente con el tipo de colindancia.
    No sobrescribe desplegables que ya tengan valor.
    """
    import random

    orientaciones = _orientaciones_desde_geojson(ruta_geojson)
    if not orientaciones:
        print("  Sin orientaciones: no se puede continuar. Verifica la ruta del GeoJSON.")
        return

    selects = page.locator("select")
    total = selects.count()
    if total == 0:
        print("  No hay desplegables. ¿Estas en la pestaña Linderos del Paso 3?")
        return
    filas = total // 2
    if filas != len(orientaciones):
        print(f"  AVISO: {filas} linderos en pantalla vs {len(orientaciones)} calculados "
              f"del poligono. Se usara el minimo y se continua.")
    nfilas = min(filas, len(orientaciones))

    # Colindancias coherentes rural: mayoria Predio, algunos Via/Rio.
    tipos = ["Predio"] * 7 + ["Vía", "Río", "Otro"]
    # Nombres sinteticos para el campo de texto segun el tipo.
    nombres_via = ["Vía Veredal El Carmen", "Camino Real La Esperanza",
                   "Vía Terciaria Potrerillo"]
    nombres_rio = ["Quebrada La Honda", "Río Claro", "Zanjón El Guabo"]

    def npn_sintetico():
        # 30 digitos: usa el prefijo municipal 7636400020 y rellena el resto.
        base = "763640002"
        resto = "".join(str(random.randint(0, 9)) for _ in range(30 - len(base)))
        return base + resto

    print(f"  Llenando {nfilas} linderos con ORIENTACION REAL del poligono...")
    hechos_or = hechos_co = hechos_txt = saltados = errores = 0

    # Desplegables: pares (orientacion, colinda con).
    for f in range(nfilas):
        sel_or = selects.nth(f * 2)
        sel_co = selects.nth(f * 2 + 1)
        # Orientacion real.
        try:
            if sel_or.input_value() in ("", None):
                sel_or.select_option(label=orientaciones[f])
                hechos_or += 1
            else:
                saltados += 1
        except Exception:
            errores += 1
        # Colinda con (aleatorio coherente).
        tipo = random.choice(tipos)
        try:
            if sel_co.input_value() in ("", None):
                sel_co.select_option(label=tipo)
                hechos_co += 1
        except Exception:
            errores += 1
        if f % 10 == 0:
            page.wait_for_timeout(120)

    # Campos de texto del NPN/nombre del colindante (un input por fila).
    inputs = page.locator("input[placeholder*='NPN del predio vecino']")
    ni = inputs.count()
    for f in range(min(ni, nfilas)):
        try:
            # Reconstruir el tipo elegido no es trivial; se usa un valor generico
            # coherente: NPN sintetico (predio) la mayoria, nombre de via/rio algunos.
            r = random.random()
            if r < 0.7:
                valor = npn_sintetico()
            elif r < 0.85:
                valor = random.choice(nombres_via)
            else:
                valor = random.choice(nombres_rio)
            caja = inputs.nth(f)
            if caja.input_value() in ("", None):
                caja.fill(valor)
                hechos_txt += 1
        except Exception:
            errores += 1
        if f % 10 == 0:
            page.wait_for_timeout(100)

    print(f"  Orientaciones aplicadas: {hechos_or} | Colinda con: {hechos_co} | "
          f"NPN/nombre: {hechos_txt}")
    print(f"  Ya tenian valor: {saltados} | errores: {errores}")
    print("  Recuerda pulsar 'Guardar' para fijar los linderos (boton Guardar).")


def editar_direccion(page, semilla: str = "") -> None:
    """Edita la direccion del predio (Paso 1) dejandola ESTRUCTURADA (LADM) y la
    llena con datos sinteticos coherentes y unicos, luego pulsa 'Actualizar'.

    Flujo:
      1. Abre el modal de editar (icono lapiz de la primera direccion) si no esta abierto.
      2. Cambia 'Tipo de direccion' a 'Estructurada'.
      3. Llena Via Principal (Clase de via, Valor, Letra), Via Generadora (Valor, Letra),
         Numero del predio y Codigo postal.
      4. Pulsa 'Actualizar'.

    Los valores numericos se generan aleatorios (no repetidos) para variar por tramite.
    'semilla' (p. ej. el radicado) fija la aleatoriedad.
    """
    import random
    import re as _re
    if semilla:
        random.seed(semilla + "-dir")

    # 0) Leer la direccion ACTUAL (antes de abrir el modal) para extraer sus numeros
    #    como pista y reutilizarlos en la direccion estructurada.
    numeros_pista = []
    try:
        cuerpo = page.locator("body").inner_text()
        # Buscar la fila de direccion y sus numeros.
        m = _re.search(r"Direcciones del Predio(.{0,400})", cuerpo, _re.S)
        zona = m.group(1) if m else cuerpo
        numeros_pista = [n for n in _re.findall(r"\b(\d{1,4})\b", zona)]
        # Evitar tomar numeros del NPN (muy largos) o años.
        numeros_pista = [n for n in numeros_pista if 1 <= int(n) <= 999][:6]
        if numeros_pista:
            print(f"  Numeros pista de la direccion anterior: {numeros_pista}")
    except Exception:
        pass

    # 1) Abrir el modal. Dos casos:
    #    a) Ya existe una direccion -> editar (icono lapiz 'edit').
    #    b) NO hay direccion (p. ej. Division con predios nuevos) -> pulsar
    #       '+ Añadir Dirección' para abrir el modal 'Nueva dirección'.
    es_nueva = False
    try:
        titulo = page.get_by_text("Editar dirección", exact=False)
        titulo_nueva = page.get_by_text("Nueva dirección", exact=False)
        if titulo.count() == 0 and titulo_nueva.count() == 0:
            lapiz = page.get_by_text("edit", exact=True)
            if lapiz.count() > 0:
                # Hay una direccion existente: editarla.
                lapiz.first.click()
                page.wait_for_timeout(800)
            else:
                # No hay direccion: anadir una nueva.
                anadir = page.get_by_role("button", name="Añadir Dirección")
                if anadir.count() == 0:
                    anadir = page.get_by_text("Añadir Dirección", exact=False)
                if anadir.count() > 0:
                    anadir.first.click()
                    page.wait_for_timeout(900)
                    es_nueva = True
                    print("  No habia direccion: se abrio '+ Anadir Direccion' (modal nuevo).")
                else:
                    print("  No se encontro ni direccion para editar ni '+ Anadir Direccion'.")
        elif titulo_nueva.count() > 0:
            es_nueva = True
    except Exception:
        pass

    # 2) Cambiar Tipo de direccion a Estructurada (el <select> del modal con esa opcion).
    selects = page.locator("select")
    sel_tipo = None
    for i in range(selects.count()):
        opts = [o.inner_text().strip() for o in
                [selects.nth(i).locator("option").nth(j) for j in
                 range(selects.nth(i).locator("option").count())]]
        if "Estructurada" in opts and "No Estructurada" in opts:
            sel_tipo = selects.nth(i)
            break
    if sel_tipo is not None:
        try:
            sel_tipo.select_option(label="Estructurada")
            page.wait_for_timeout(900)  # aparecen los campos estructurados
            print("  Tipo de direccion = Estructurada")
        except Exception as e:
            print(f"  No se pudo cambiar a Estructurada: {type(e).__name__}")
    else:
        print("  No se encontro el desplegable 'Tipo de direccion' del modal.")

    # Re-leer selects tras cambiar a estructurada (aparecen clase de via, sectores).
    selects = page.locator("select")

    def elegir_por_opciones(contiene_set: set, valor: str) -> bool:
        """Elige en el <select> cuyas opciones contengan las palabras dadas."""
        for i in range(selects.count()):
            try:
                opts = [selects.nth(i).locator("option").nth(j).inner_text().strip()
                        for j in range(selects.nth(i).locator("option").count())]
            except Exception:
                continue
            joined = " ".join(opts).lower()
            if all(c.lower() in joined for c in contiene_set):
                try:
                    selects.nth(i).select_option(label=valor)
                    return True
                except Exception:
                    # fallback: primera opcion valida
                    for t in opts:
                        if t and not t.startswith("—") and not t.lower().startswith("seleccione"):
                            selects.nth(i).select_option(label=t)
                            return True
        return False

    # 3) Clase de via (Calle/Carrera/...). Elegimos una coherente al azar.
    clase = random.choice(["Calle", "Carrera", "Diagonal", "Transversal", "Avenida"])
    if elegir_por_opciones({"Calle", "Carrera"}, clase):
        print(f"  Clase de via = {clase}")
    else:
        print("  No se encontro 'Clase de via'.")

    # Valores numericos coherentes y unicos. Si hay numeros pista de la direccion
    # anterior, se reutiliza alguno (coherencia con el dato de origen).
    def _pista_o_random(maximo: int, usados: set) -> str:
        candidatos = [n for n in numeros_pista if n not in usados and 1 <= int(n) <= maximo]
        if candidatos:
            elegido = random.choice(candidatos)
            usados.add(elegido)
            return elegido
        return str(random.randint(1, maximo))

    _usados_pista: set = set()
    # Generar direcciones unicas entre tramites (set global _direcciones_usadas).
    for _ in range(50):
        vp_valor = _pista_o_random(120, _usados_pista)
        vp_letra = random.choice(["", "A", "B", "C"])
        vg_valor = _pista_o_random(90, _usados_pista)
        vg_letra = random.choice(["", "A", "B"])
        num_predio = _pista_o_random(99, _usados_pista)
        firma = f"{vp_valor}{vp_letra}-{vg_valor}{vg_letra}-{num_predio}"
        if firma not in _direcciones_usadas:
            _direcciones_usadas.add(firma)
            break
    cod_postal = f"76{random.randint(1000, 9999)}"  # 6 digitos, prefijo Valle

    # 4) Llenar los campos de texto por placeholder (del modal).
    def fill_ph(ph: str, valor: str, etiqueta: str):
        loc = page.locator(f"input[placeholder='{ph}']")
        if loc.count() > 0:
            try:
                loc.first.fill(valor)
                print(f"  {etiqueta} = {valor!r}")
                return
            except Exception:
                pass
    # Via principal: Valor (Ej: 10), Letra (Ej: A primera).
    fill_ph("Ej: 10", vp_valor, "Via principal valor")
    letras = page.locator("input[placeholder='Ej: A']")
    if letras.count() > 0 and vp_letra:
        letras.nth(0).fill(vp_letra); print(f"  Via principal letra = {vp_letra!r}")
    # Via generadora: Valor (Ej: 5), Letra (Ej: A segunda).
    fill_ph("Ej: 5", vg_valor, "Via generadora valor")
    if letras.count() > 1 and vg_letra:
        letras.nth(1).fill(vg_letra); print(f"  Via generadora letra = {vg_letra!r}")
    # Numero del predio (Ej: 42) y codigo postal (6 digitos).
    fill_ph("Ej: 42", num_predio, "Numero del predio")
    fill_ph("6 dígitos", cod_postal, "Codigo postal")

    page.wait_for_timeout(500)

    # 5) Pulsar el boton PRIMARIO del modal (Agregar / Actualizar).
    #    El boton es <button class="... bg-primary ..."><span>save</span>Agregar</button>,
    #    asi que su innerText es "saveAgregar": NO se puede anclar ^Agregar$. Se busca el
    #    boton primario azul cuyo texto TERMINA en 'Agregar'/'Actualizar' (no 'Agregar
    #    foto' ni 'Agregar segmento', que no son bg-primary).
    nombres_boton = (["Agregar", "Actualizar", "Guardar"] if es_nueva
                     else ["Actualizar", "Agregar", "Guardar"])
    pulsado = False
    for nb in nombres_boton:
        # Primario azul que termina en el nombre (tolera el icono 'save' al inicio).
        cand = page.locator("button.bg-primary").filter(
            has_text=_re.compile(rf"{nb}\s*$"))
        if cand.count() == 0:
            cand = page.get_by_role("button", name=nb)
        if cand.count() > 0:
            try:
                btn = cand.last  # el del modal suele ser el ultimo en el DOM
                btn.wait_for(state="visible", timeout=4000)
                btn.scroll_into_view_if_needed()
                btn.click()
                page.wait_for_timeout(1300)
                page.wait_for_load_state("networkidle")
                accion = "AGREGADA" if es_nueva else "ACTUALIZADA"
                print(f"  Direccion estructurada {accion} (boton '{nb}'): {clase} "
                      f"{vp_valor}{vp_letra} # {vg_valor}{vg_letra} - {num_predio}, CP {cod_postal}")
                pulsado = True
                break
            except Exception as e:
                print(f"  [dir] intento boton '{nb}' fallo: {type(e).__name__}")
                continue
    if not pulsado:
        print("  No se encontro el boton primario para guardar la direccion. Revisa el modal.")


# Datos de propietarios sinteticos ya usados (para NO repetir entre tramites).
_propietarios_usados_doc: set = {"1130598742"}
_propietarios_usados_nombre: set = set()

_NOMBRES_M = ["Juan", "Carlos", "Andres", "Santiago", "Felipe", "Mauricio", "Diego",
              "Ricardo", "Oscar", "Javier", "Hernan", "Alberto", "Sergio", "Fabian",
              "Camilo", "Esteban", "Julian", "Mateo", "Ivan", "Hugo"]
_NOMBRES_F = ["Maria", "Luisa", "Carolina", "Patricia", "Diana", "Angela", "Paola",
              "Natalia", "Catalina", "Sandra", "Liliana", "Marcela", "Adriana", "Claudia",
              "Daniela", "Valentina", "Lorena", "Monica", "Ximena", "Beatriz"]
_APELLIDOS = ["Ramirez", "Gomez", "Lopez", "Martinez", "Rodriguez", "Gonzalez", "Perez",
              "Torres", "Vargas", "Castro", "Ospina", "Valencia", "Zuluaga", "Cardenas",
              "Montoya", "Giraldo", "Arango", "Quintero", "Restrepo", "Mejia", "Salazar",
              "Rios", "Cuellar", "Bedoya", "Agudelo", "Marin", "Ocampo", "Serna"]


def _nueva_persona_unica(rnd, sexo: str = "") -> dict:
    """Genera una persona natural unica (nombre + documento no repetidos).

    sexo: '' = aleatorio; 'femenino'/'f' = fuerza mujer; 'masculino'/'m' = fuerza hombre.
    """
    sx = (sexo or "").strip().lower()
    for _ in range(300):
        if sx.startswith("f"):
            es_m = False
        elif sx.startswith("m"):
            es_m = True
        else:
            es_m = rnd.random() < 0.5
        n1 = rnd.choice(_NOMBRES_M if es_m else _NOMBRES_F)
        n2 = rnd.choice(_NOMBRES_M if es_m else _NOMBRES_F)
        a1 = rnd.choice(_APELLIDOS)
        a2 = rnd.choice(_APELLIDOS)
        nombre = f"{n1} {n2} {a1} {a2}"
        doc = str(rnd.randint(10_000_000, 1_299_999_999))
        if nombre.lower() in _propietarios_usados_nombre or doc in _propietarios_usados_doc:
            continue
        _propietarios_usados_nombre.add(nombre.lower())
        _propietarios_usados_doc.add(doc)
        return {"n1": n1, "n2": n2, "a1": a1, "a2": a2, "doc": doc,
                "sexo": "Masculino" if es_m else "Femenino"}
    doc = str(rnd.randint(10_000_000, 1_299_999_999))
    sexo_fb = "Femenino" if sx.startswith("f") else "Masculino"
    return {"n1": "Prueba", "n2": "Qa", "a1": "Test", "a2": str(doc[-3:]),
            "doc": doc, "sexo": sexo_fb}


def _select_spa(page, idx: int, etiqueta_opcion: str) -> bool:
    """Selecciona una opcion en el <select> idx DISPARANDO el evento change que la SPA
    (React/Vue) necesita. Resuelve que el valor quede en 'None' aunque se vea bien."""
    selects = page.locator("select")
    if idx >= selects.count():
        return False
    try:
        selects.nth(idx).select_option(label=etiqueta_opcion)
    except Exception:
        return False
    try:
        selects.nth(idx).evaluate(
            "el => { el.dispatchEvent(new Event('input',{bubbles:true}));"
            " el.dispatchEvent(new Event('change',{bubbles:true})); }")
    except Exception:
        pass
    page.wait_for_timeout(250)
    return True


def _idx_select_con(page, *palabras) -> int:
    """Indice del <select> cuyas opciones contengan TODAS las palabras."""
    selects = page.locator("select")
    for i in range(selects.count()):
        try:
            opts = [selects.nth(i).locator("option").nth(j).inner_text().strip()
                    for j in range(selects.nth(i).locator("option").count())]
        except Exception:
            continue
        joined = " ".join(opts).lower()
        if all(w.lower() in joined for w in palabras):
            return i
    return -1


def _eliminar_propietarios_existentes(page) -> int:
    """Elimina TODOS los propietarios de la tabla (icono papelera 'delete').
    Devuelve cuantos elimino. Maneja posible modal de confirmacion."""
    eliminados = 0
    for _ in range(10):
        papeleras = page.get_by_text("delete", exact=True)
        if papeleras.count() == 0:
            break
        try:
            papeleras.first.click()
            page.wait_for_timeout(700)
            for txt in ("Eliminar", "Confirmar", "Sí", "Aceptar"):
                btn = page.get_by_role("button", name=txt)
                if btn.count() > 0:
                    btn.first.click()
                    page.wait_for_timeout(600)
                    break
            eliminados += 1
            page.wait_for_load_state("networkidle")
        except Exception:
            break
    return eliminados


def _llenar_interesado(page, p: dict, participacion) -> None:
    """Llena 'Datos del Nuevo Interesado' con la persona p y el % indicado, y pulsa
    'Agregar Propietario'. Usa _select_spa para que los desplegables registren el valor."""
    i = _idx_select_con(page, "Persona Natural", "Persona Jurídica")
    if i < 0:
        print("  No se encontro 'Tipo Interesado'. ¿Es el Paso 2 de Cambio de Propietario?")
        return
    _select_spa(page, i, "Persona Natural")
    print("  Tipo Interesado = Persona Natural")
    page.wait_for_timeout(700)

    i = _idx_select_con(page, "Cédula de Ciudadanía")
    if i >= 0:
        _select_spa(page, i, "Cédula de Ciudadanía")
        print("  Tipo de Documento = Cédula de Ciudadanía")

    textos = page.locator("input[type='text'], input:not([type])")

    def fill_idx(idx, valor):
        try:
            if idx < textos.count():
                textos.nth(idx).fill(valor)
                return True
        except Exception:
            pass
        return False
    fill_idx(0, p["doc"])
    fill_idx(2, p["n1"])
    fill_idx(3, p["n2"])
    fill_idx(4, p["a1"])
    fill_idx(5, p["a2"])
    print(f"  Interesado = {p['n1']} {p['n2']} {p['a1']} {p['a2']} ({p['sexo']}) doc {p['doc']}")

    i = _idx_select_con(page, "Masculino", "Femenino")
    if i >= 0:
        _select_spa(page, i, p["sexo"])
        print(f"  Sexo = {p['sexo']}")
    i = _idx_select_con(page, "Afrocolombiano")
    if i >= 0:
        _select_spa(page, i, "Ninguno")
        print("  Autorreconocimiento étnico = Ninguno")
    i = _idx_select_con(page, "Dominio", "Usufructo")
    if i >= 0:
        _select_spa(page, i, "Dominio")
        print("  Tipo Derecho = Dominio")

    try:
        caja = page.locator("input[type='number']")
        if caja.count() > 0:
            caja.last.fill(str(participacion))
            caja.last.evaluate(
                "el => { el.dispatchEvent(new Event('input',{bubbles:true}));"
                " el.dispatchEvent(new Event('change',{bubbles:true})); }")
    except Exception:
        pass
    print(f"  % Participación = {participacion}")

    try:
        page.keyboard.press("Tab")
    except Exception:
        pass
    page.wait_for_timeout(900)

    def filas():
        try:
            return page.locator("table tbody tr").count()
        except Exception:
            return 0
    antes = filas()
    boton = page.get_by_role("button", name="Agregar Propietario")
    if boton.count() == 0:
        boton = page.locator("button", has_text="Agregar Propietario")
    if boton.count() > 0:
        boton.first.click()
        page.wait_for_timeout(1500)
        page.wait_for_load_state("networkidle")
        print(f"  'Agregar Propietario' -> filas: {antes} -> {filas()}")
    else:
        print("  No se encontro el boton 'Agregar Propietario'.")


def nuevo_propietario(page, semilla: str = "", participacion: str = "100",
                      modo: str = "sustitucion", copropietarios: int = 1,
                      sexo: str = "") -> None:
    """Paso 2 de Cambio de Propietario, con dos ramas:

    modo='sustitucion' (MODO_SUSTITUCION_100): ELIMINA los titulares previos y registra
        UN nuevo titular al % indicado (def. 100).
    modo='copropiedad' (MODO_INCORPORACION_COPROPIEDAD): NO elimina; agrega N nuevos
        copropietarios repartiendo el 100% en partes iguales. 'copropietarios' = cuantos.

    Datos sinteticos UNICOS por titular. Los <select> se fijan con evento change.
    """
    import random
    rnd = random.Random(semilla + "-prop") if semilla else random.Random()

    if modo.lower().startswith("sust"):
        n = _eliminar_propietarios_existentes(page)
        print(f"  MODO SUSTITUCION: eliminados {n} propietario(s) previo(s).")
        page.wait_for_timeout(600)
        p = _nueva_persona_unica(rnd, sexo)
        _llenar_interesado(page, p, participacion)
    else:
        total = max(1, int(copropietarios))
        base = 100 // total
        cuotas = [base] * total
        cuotas[-1] += 100 - base * total
        print(f"  MODO COPROPIEDAD: {total} nuevos titulares, cuotas {cuotas} (suma 100).")
        for k in range(total):
            p = _nueva_persona_unica(rnd, sexo)
            print(f"  -- Copropietario {k+1}/{total} ({cuotas[k]}%) --")
            _llenar_interesado(page, p, str(cuotas[k]))
            page.wait_for_timeout(800)


def _direccion_es_estructurada(page) -> bool:
    """True si la direccion principal del predio ya es Estructurada (no hay que tocarla).

    Lee el tipo desde la CELDA de la tabla 'Direcciones del Predio' (columna TIPO),
    no del cuerpo completo (mas robusto). Por seguridad, ante cualquier duda devuelve
    True (preferir NO editar una direccion que ya existe)."""
    try:
        # Celdas de la primera columna (TIPO) de la tabla de direcciones.
        filas = page.locator("table tbody tr")
        for i in range(filas.count()):
            t = filas.nth(i).inner_text()
            if "Estructurada" in t or "Carrera" in t or "Calle" in t or "Avenida" in t:
                if "No Estructurada" in t:
                    return False
                if "Estructurada" in t:
                    return True
        # Si no se pudo determinar por la tabla, revisar el cuerpo.
        cuerpo = page.locator("body").inner_text()
        if "No Estructurada" in cuerpo:
            return False
        if "Estructurada" in cuerpo:
            return True
    except Exception:
        pass
    # Ante la duda, NO editar (asumir estructurada).
    return True


def _editar_calificacion_uc(page, semilla: str = "") -> bool:
    """En el Paso 4 (Construccion), abre la EDICION de la UC existente (icono/boton
    'edit') y complementa su calificacion catastral con 'llenar_construccion', luego
    pulsa 'Actualizar'/'Guardar'. Para Cambio de Destino la geometria YA coincide, solo
    se completa lo alfanumerico. Devuelve True si edito algo."""
    # Abrir el editor de la UC existente.
    abierto = False
    try:
        lapiz = page.get_by_text("edit", exact=True)
        if lapiz.count() > 0:
            lapiz.first.click()
            page.wait_for_timeout(900)
            abierto = True
    except Exception:
        pass
    if not abierto:
        # Respaldo: boton con texto Editar.
        try:
            b = page.get_by_role("button", name="Editar")
            if b.count() > 0:
                b.first.click()
                page.wait_for_timeout(900)
                abierto = True
        except Exception:
            pass
    if not abierto:
        print("  [aviso] no se encontro el boton de editar la UC. Revisa con 'cap'.")
        return False
    # Completar la calificacion (reutiliza la logica de llenar_construccion: tipo/uso/
    # estado/calificacion conservadora). NO toca geometria.
    try:
        llenar_construccion(page, "", semilla)
    except Exception as e:
        print(f"  [aviso] al completar calificacion: {type(e).__name__}")
    # Guardar/Actualizar la UC.
    for txt in ("Actualizar", "Guardar", "Actualizar UC", "Guardar UC"):
        b = page.get_by_role("button", name=txt)
        if b.count() == 0:
            b = page.locator("button", has_text=txt)
        if b.count() > 0:
            b.first.click()
            page.wait_for_timeout(1200)
            page.wait_for_load_state("networkidle")
            print(f"  Calificacion de la UC guardada ('{txt}').")
            return True
    print("  [aviso] no se encontro boton Actualizar/Guardar de la UC.")
    return False


def tramite3a_completo(page, semilla: str = "", destino: str = "",
                       anio_avaluo: str = "2025", editar_uc: bool = True) -> None:
    """Mutacion 3a (Cambio Destino Economico / Cambio Area Construida) de CORRIDO.

    Para Cambio de Destino: el terreno NO cambia (solo avanzar) y la construccion YA
    tiene geometria coincidente; se EDITA la calificacion de la UC (alfanumerico) y se
    actualiza. Luego avanza Fuente Admin + Avaluo + Resumen validando. NO pasa a calidad.

    - Paso 1: direccion (solo si NO es estructurada) + destino (solo si se indica).
    - Paso 2: propietario (no toca).
    - Paso 3 Terreno: NO se pausa; se avanza (sin cambios graficos).
    - Paso 4 Construccion: si editar_uc, edita la calificacion de la UC existente.
    - Paso 5/6: Fuente Admin + Avaluo. Paso 7: Resumen validando.
    """
    import re as _re
    # Paso 1.
    if _direccion_es_estructurada(page):
        print("  Direccion YA estructurada: no se toca.")
    else:
        print("  Direccion NO estructurada: se estructura.")
        editar_direccion(page, semilla)
        page.wait_for_timeout(800)
    if destino:
        cambiar_destino(page, destino)
    else:
        print("  Destino Económico: se mantiene el actual (coherente con la direccion).")

    # Recorrer TODO el wizard de corrido hasta el Resumen. En el Paso 3 (Terreno) y el
    # Paso 4 (Construccion) solo se AVANZA (no se carga geometria ni se edita la UC): el
    # usuario ajustara la construccion al final. Paso 5 Fuente Admin, Paso 6 Avaluo.
    for _ in range(18):
        n = detectar_paso(page)
        if n is None or n >= 7:
            break
        if n == 3:
            print("  Paso 3 Terreno: se avanza (sin cambios).")
        elif n == 4:
            print("  Paso 4 Construccion: se avanza (el usuario ajustara la UC al final).")
        elif n == 5:
            try:
                fuente_administrativa(page, semilla)
            except Exception:
                pass
        elif n == 6:
            try:
                calcular_avaluo(page, anio_avaluo)
            except Exception:
                pass
        continuar_wizard(page)
        page.wait_for_timeout(1300)

    # Resumen: re-validar y leer conteo.
    try:
        rev = page.get_by_role("button", name="Re-validar")
        if rev.count() == 0:
            rev = page.locator("button", has_text="validar")
        if rev.count() > 0:
            rev.first.click()
            page.wait_for_timeout(2500)
            page.wait_for_load_state("networkidle")
    except Exception:
        pass
    try:
        cuerpo = page.locator("body").inner_text()
        def _c(etq):
            m = _re.search(r"(\d+)\s*[\r\n]+\s*" + etq, cuerpo, _re.IGNORECASE)
            return m.group(1) if m else None
        err = _c("ERRORES")
        print(f"  VALIDACIONES -> errores: {err or '?'} | warnings: {_c('WARNINGS') or '?'} "
              f"| ok: {_c('OK') or '?'}")
        if err == "0":
            print("  >>> 0 ERRORES. Listo para 'Pasar borrador acto administrativo' (lo confirma el usuario).")
        elif err is not None:
            print(f"  >>> HAY {err} ERROR(ES). Probablemente la construccion (geometria/altura/")
            print("  >>> calificacion): el usuario debe AJUSTARLA al final (Paso 4) y re-validar.")
    except Exception:
        pass
    print("  (El comando NO pasa a calidad automaticamente.)")


def tramite3a_fin(page, semilla: str = "", anio_avaluo: str = "2025") -> None:
    """Mutacion 3a - PARTE 2 (tras cargar la geometria de la construccion):
    Paso 4: edita la calificacion de la UC existente (boton edit) + Actualizar. Luego
    Fuente Admin + Avaluo + Resumen validando. NO pasa a calidad.
    """
    import re as _re
    # Paso 4: editar calificacion de la UC existente.
    n = detectar_paso(page)
    if n == 4:
        print("  Paso 4: editando calificacion de la UC (la geometria ya la cargo el usuario)...")
        _editar_calificacion_uc(page, semilla)
        page.wait_for_timeout(800)
    # Avanzar hasta el Resumen.
    for _ in range(16):
        n = detectar_paso(page)
        if n is None or n >= 7:
            break
        if n == 5:
            try:
                fuente_administrativa(page, semilla)
            except Exception:
                pass
        elif n == 6:
            try:
                calcular_avaluo(page, anio_avaluo)
            except Exception:
                pass
        continuar_wizard(page)
        page.wait_for_timeout(1300)

    # Resumen: re-validar y leer conteo.
    try:
        rev = page.get_by_role("button", name="Re-validar")
        if rev.count() == 0:
            rev = page.locator("button", has_text="validar")
        if rev.count() > 0:
            rev.first.click()
            page.wait_for_timeout(2500)
            page.wait_for_load_state("networkidle")
    except Exception:
        pass
    try:
        cuerpo = page.locator("body").inner_text()
        def _c(etq):
            m = _re.search(r"(\d+)\s*[\r\n]+\s*" + etq, cuerpo, _re.IGNORECASE)
            return m.group(1) if m else None
        err = _c("ERRORES")
        print(f"  VALIDACIONES -> errores: {err or '?'} | warnings: {_c('WARNINGS') or '?'} "
              f"| ok: {_c('OK') or '?'}")
        if err == "0":
            print("  >>> 0 ERRORES. Listo para 'Pasar borrador acto administrativo' y calidad (lo confirma el usuario).")
        elif err is not None:
            print(f"  >>> HAY {err} ERROR(ES): revisar antes de calidad.")
    except Exception:
        pass
    print("  (El comando NO pasa a calidad automaticamente.)")


def _valor_sintetico_para(nombre: str, tipo: str, rnd) -> str:
    """Devuelve un valor sintetico coherente segun el nombre/placeholder y el tipo de
    input, aplicando reglas catastrales basicas."""
    n = (nombre or "").lower()
    if tipo == "date":
        anio = rnd.randint(2008, 2022)
        return f"{anio:04d}-{rnd.randint(1,12):02d}-{rnd.randint(1,28):02d}"
    if "matric" in n or "folio" in n:
        return str(rnd.randint(100000, 999999))        # matricula: solo numerica
    if "npn" in n or "predial" in n:
        return ""  # NO inventar NPN en campos sueltos
    # Placeholders de ejemplo NUMERICO (p. ej. "Ej: 12345", "Ej: 100"): el campo espera
    # un numero aunque sea type=text. Devolver solo digitos (evita "QA 890" en matricula).
    import re as _re_v
    m_ej = _re_v.search(r"ej[:\.]?\s*(\d+)", n)
    if m_ej:
        ejemplo = m_ej.group(1)
        return str(rnd.randint(10 ** (len(ejemplo) - 1), 10 ** len(ejemplo) - 1))
    if "anio" in n or "año" in n or "year" in n:
        return str(rnd.randint(1990, 2020))
    if "area" in n or "área" in n:
        return str(rnd.randint(40, 500))
    if "%" in n or "particip" in n or "porcentaje" in n:
        return "100"
    if "documento" in n or "cedula" in n or "nit" in n:
        return str(rnd.randint(10_000_000, 1_299_999_999))
    if tipo == "number":
        return str(rnd.randint(1, 50))
    if "observ" in n or "descrip" in n or "nota" in n:
        return "sin observacion"
    if "nombre" in n or "razon" in n or "razón" in n:
        # Nombre coherente (no 'QA ...'): nombre + apellido reales al azar.
        return f"{rnd.choice(_NOMBRES_M + _NOMBRES_F)} {rnd.choice(_APELLIDOS)}"
    if "correo" in n or "email" in n or "mail" in n:
        return f"contacto{rnd.randint(100,999)}@ejemplo.com"
    if "tel" in n or "celular" in n or "movil" in n or "móvil" in n:
        return f"3{rnd.randint(100000000, 199999999)}"
    # Campo de texto NO reconocido: no inventar basura (evita 'QA ...'). Dejar vacio;
    # si fuera obligatorio, la plataforma lo marcara y se resuelve de forma dirigida.
    return ""


def autopaso(page, semilla: str = "") -> dict:
    """Inspeccion DINAMICA del paso actual: escanea inputs/select/textarea/checkbox,
    clasifica editable vs bloqueado (disabled/readonly) y LLENA los editables vacios con
    datos sinteticos coherentes. NO toca campos readonly/disabled ni geometria.

    Devuelve un dict con el mapeo {editados:[...], bloqueados:[...]} para el resumen.
    """
    import random
    rnd = random.Random((semilla or "") + "-auto-" + str(random.random()))
    editados, bloqueados = [], []

    # 1) SELECTS editables: elegir primera opcion valida (no placeholder), con change.
    #    EXCEPCION: no tocar los selects de caracterizacion LADM (Tipo de Predio,
    #    Tipo de Derecho) ni Destino Economico: los pone el flujo dirigido con los
    #    valores correctos (Privado/Dominio/...). El generico los pisaria con la 1a
    #    opcion (p. ej. "Publico - Baldio" / "Derecho de Propiedad Colectiva"), mal.
    selects = page.locator("select")
    for i in range(selects.count()):
        s = selects.nth(i)
        try:
            dis = s.is_disabled()
            ro = s.get_attribute("readonly") is not None
            if dis or ro:
                bloqueados.append(f"select#{i}")
                continue
            if (s.input_value() or "") not in ("", None):
                continue  # ya tiene valor, no lo piso
            opts = [s.locator("option").nth(j).inner_text().strip()
                    for j in range(s.locator("option").count())]
            _joined = " ".join(opts)
            # Saltar selects sensibles (caracterizacion / destino).
            es_tipo_predio = ("Privado" in opts and ("Baldío" in _joined or "Baldio" in _joined))
            es_tipo_derecho = ("Dominio" in opts and ("Usufructo" in opts or "Nuda Propiedad" in opts))
            es_destino = ("Habitacional" in opts and "Comercial" in opts)
            if es_tipo_predio or es_tipo_derecho or es_destino:
                bloqueados.append(f"select#{i}(caracterizacion/destino: protegido)")
                continue
            objetivo = None
            for t in opts:
                tl = t.lower()
                if t and "seleccione" not in tl and "sin selec" not in tl \
                   and not t.startswith("—") and "primero" not in tl and "usos de" not in tl:
                    objetivo = t
                    break
            if objetivo:
                s.select_option(label=objetivo)
                s.evaluate("el => { el.dispatchEvent(new Event('input',{bubbles:true}));"
                           " el.dispatchEvent(new Event('change',{bubbles:true})); }")
                editados.append(f"select#{i}={objetivo}")
        except Exception:
            bloqueados.append(f"select#{i}(err)")

    # 2) INPUTS de texto/numero/fecha editables.
    inputs = page.locator("input")
    for i in range(inputs.count()):
        el = inputs.nth(i)
        try:
            tipo = (el.get_attribute("type") or "text").lower()
            if tipo in ("hidden", "file", "radio", "submit", "button", "image"):
                continue
            dis = el.is_disabled()
            ro = el.get_attribute("readonly") is not None
            if dis or ro:
                bloqueados.append(f"input[{tipo}]#{i}")
                continue
            if tipo == "checkbox":
                continue  # no marcar checkboxes por defecto (pueden ser sensibles)
            if (el.input_value() or "") not in ("", None, "0"):
                continue
            nombre = (el.get_attribute("placeholder") or el.get_attribute("name")
                      or el.get_attribute("aria-label") or "")
            valor = _valor_sintetico_para(nombre, tipo, rnd)
            if valor == "":
                continue
            el.fill(valor)
            el.evaluate("el => { el.dispatchEvent(new Event('input',{bubbles:true}));"
                        " el.dispatchEvent(new Event('change',{bubbles:true})); }")
            editados.append(f"input[{tipo}]#{i}={valor}")
        except Exception:
            bloqueados.append(f"input#{i}(err)")

    # 3) TEXTAREAS editables -> 'sin observacion'.
    tas = page.locator("textarea")
    for i in range(tas.count()):
        t = tas.nth(i)
        try:
            if t.is_disabled() or t.get_attribute("readonly") is not None:
                bloqueados.append(f"textarea#{i}")
                continue
            if (t.input_value() or "") in ("", None):
                t.fill("sin observacion")
                editados.append(f"textarea#{i}")
        except Exception:
            pass

    print(f"  [autopaso] editados: {len(editados)} | bloqueados: {len(bloqueados)}")
    return {"editados": editados, "bloqueados": bloqueados}


def seleccionar_predio(page, clave: str) -> bool:
    """Selecciona un predio del panel 'LISTADO DE PREDIOS' clicando el <button> que lo
    contiene. 'clave' puede ser el NPN (30 digitos) o el numero de predio (p. ej. 112071).

    IMPORTANTE: cada predio del listado es un <button> cuyo texto incluye el NPN y
    'Predio #<num>'. Hay que clicar el BUTTON (no el <p> interno) para que React cambie
    el predio activo. OJO: el desplegable 'Copiar propietarios de...' del Paso 2 NO
    cambia el predio activo; no usarlo para eso.
    """
    clave = (clave or "").strip()
    if not clave:
        print("  Uso: predio <NPN o numero de predio>")
        return False
    # Buscar el <button> del listado que contenga la clave en su texto.
    botones = page.locator("button", has_text=clave)
    # Filtrar a los que parezcan tarjeta de predio (contienen 'Predio #' o un NPN largo).
    objetivo = None
    for i in range(botones.count()):
        try:
            txt = botones.nth(i).inner_text()
        except Exception:
            continue
        if "Predio #" in txt or _re_npn_match(txt):
            objetivo = botones.nth(i)
            break
    if objetivo is None and botones.count() > 0:
        objetivo = botones.first
    if objetivo is None:
        print(f"  No se encontro el predio '{clave}' en el listado.")
        return False
    try:
        objetivo.scroll_into_view_if_needed()
        objetivo.click()
        page.wait_for_timeout(1200)
        page.wait_for_load_state("networkidle")
        print(f"  Predio seleccionado: {clave}")
        return True
    except Exception as e:
        print(f"  No se pudo seleccionar el predio: {type(e).__name__}")
        return False


def _re_npn_match(txt: str) -> bool:
    import re as _r
    return _r.search(r"\d{25,30}", txt or "") is not None


def tramite_auto(page, semilla: str = "", anio_avaluo: str = "2025",
                 destino: str = "") -> dict:
    """Motor AUTO-ADAPTATIVO: recorre el wizard de corrido hasta el Resumen aplicando
    inspeccion dinamica (autopaso) en cada paso. Reglas:
      - Llena todo lo alfanumerico editable (datos sinteticos coherentes).
      - Geometria (terreno/construccion): NO la carga (reserva del usuario); avanza.
      - Paso de Avaluo: intenta 'Calcular retroactivo' con el año dado.
      - NO pasa a calidad: se detiene en el Resumen.
    Devuelve el mapeo acumulado para el resumen.txt.
    """
    import re as _re
    mapeo = {"editados": [], "bloqueados": [], "pasos": []}
    visto = {}
    for _ in range(24):
        try:
            cuerpo = page.locator("body").inner_text()
        except Exception:
            cuerpo = ""
        # Detectar el Resumen por textos que SOLO existen alli. OJO: NO usar
        # "Resumen Final" a secas, porque el BOTON del Paso 4 dice "Siguiente: Resumen
        # Final" y haria salir del bucle estando aun en Construccion.
        en_resumen = ("Resumen Final de la Mutaci" in cuerpo
                      or "Validaciones del tr" in cuerpo
                      or "Revise los cambios aplicados" in cuerpo)
        if en_resumen:
            break
        n = detectar_paso(page)
        clave = n if n is not None else cuerpo[:40]
        visto[clave] = visto.get(clave, 0) + 1
        if visto[clave] > 4:
            print(f"  [auto] estancado en paso {n}; se detiene.")
            break
        # Paso 4 (Construccion) de un LOTE sin construccion: no hay nada que cargar;
        # avanzar directo con 'Siguiente: Resumen Final'. La geometria de construccion es
        # reserva del usuario, pero si no hay UC el lote pasa al Resumen sin cargar nada.
        if n == 4 and "Sin unidades de construcci" in cuerpo:
            print("  [auto] Paso 4 lote sin construccion: avanzar a Resumen Final.")
            continuar_wizard(page)
            page.wait_for_timeout(1500)
            continue
        # Avaluo: calcular retroactivo si hay desplegable de vigencia + boton.
        hay_avaluo = ("Calcular retroactivo" in cuerpo) or ("AVALÚO RETROACTIVO" in cuerpo.upper())
        if hay_avaluo:
            try:
                calcular_avaluo(page, anio_avaluo)
            except Exception:
                pass
        else:
            # Paso 1 (Predio): llenado DIRIGIDO de los campos sensibles, que el
            # autopaso generico no debe tocar ni sabe poner bien:
            #   a) Caracterizacion LADM -> Privado / Dominio (no la 1a opcion = Baldio).
            #   b) Direccion -> si no hay, agregar una estructurada UNICA (modal aparte).
            # El resto (matricula numerica, etc.) lo pone el autopaso.
            if n == 1:
                try:
                    caracterizacion_ladm(page, "Privado", "Dominio")
                except Exception as e:
                    print(f"  [auto] caracterizacion: {type(e).__name__}")
                # Destino Economico coherente. Si se indico uno, usarlo. Si NO, y el
                # predio no tendra construccion (lote de Division/Segregacion), usar
                # 'Lote Urbanizado No Construido' para no disparar CUSTOM_DESTINO_REQUIERE_UC
                # (destino Habitacional/Comercial/Industrial EXIGE una unidad de construccion).
                destino_obj = destino or "Lote Urbanizado No Construido"
                try:
                    cambiar_destino(page, destino_obj)
                except Exception as e:
                    print(f"  [auto] destino: {type(e).__name__}")
                if "Sin direcciones registradas" in cuerpo:
                    try:
                        print("  [auto] Paso 1 sin direccion: se agrega una estructurada.")
                        editar_direccion(page, semilla)
                        page.wait_for_timeout(900)
                    except Exception as e:
                        print(f"  [auto] no se pudo agregar direccion: {type(e).__name__}")
            # Paso 2 (Propietario): este tipo usa el formulario 'Datos del Nuevo
            # Interesado' + boton 'Agregar Propietario', que el autopaso generico NO sabe
            # manejar. Si el predio no tiene propietario, usar nuevo_propietario (datos
            # reales unicos por semilla). NO el generico.
            paso2_propietario = (n == 2) or ("Datos del Nuevo Interesado" in cuerpo
                                             and "Agregar Propietario" in cuerpo)
            falta_prop = ("Sin propietarios registrados" in cuerpo
                          or "no tiene propietario diligenciado" in cuerpo
                          or "Falta diligenciar el propietario" in cuerpo)
            # Paso 5 (Fuente Administrativa): los 7 desplegables cargan sus opciones de
            # forma ASINCRONA; el autopaso generico llega antes y los deja vacios. Usar
            # fuente_administrativa (espera a que haya opciones). Patron ya conocido.
            paso5_fuente = (n == 5) or ("Fuente Administrativa" in cuerpo
                                        and "Naturaleza Jur" in cuerpo
                                        and "Estado de Disponibilidad" in cuerpo)
            if paso2_propietario and falta_prop:
                try:
                    print("  [auto] Paso 2: agregando propietario (datos reales unicos).")
                    nuevo_propietario(page, semilla, "100", "sustitucion", 1)
                    page.wait_for_timeout(900)
                except Exception as e:
                    print(f"  [auto] no se pudo agregar propietario: {type(e).__name__}")
                # No correr el generico en este paso (evita pisar selects del formulario).
                r = {"editados": [], "bloqueados": []}
            elif paso5_fuente:
                try:
                    print("  [auto] Paso 5: llenando Fuente Administrativa (espera async).")
                    fuente_administrativa(page, semilla)
                    page.wait_for_timeout(600)
                except Exception as e:
                    print(f"  [auto] fuente administrativa: {type(e).__name__}")
                r = {"editados": [], "bloqueados": []}
            else:
                r = autopaso(page, semilla)
            mapeo["editados"] += r["editados"]
            mapeo["bloqueados"] += r["bloqueados"]
        mapeo["pasos"].append(n)
        continuar_wizard(page)
        page.wait_for_timeout(1300)

    # Resumen: re-validar y leer conteo.
    try:
        rev = page.get_by_role("button", name="Re-validar")
        if rev.count() == 0:
            rev = page.locator("button", has_text="validar")
        if rev.count() > 0:
            rev.first.click()
            page.wait_for_timeout(2500)
            page.wait_for_load_state("networkidle")
    except Exception:
        pass
    try:
        cuerpo = page.locator("body").inner_text()
        def _c(etq):
            # Formato bloque: "N\nETIQUETA" o "ETIQUETA\nN".
            m = _re.search(r"(\d+)\s*[\r\n]+\s*" + etq, cuerpo, _re.IGNORECASE)
            if not m:
                m = _re.search(etq + r"\s*[\r\n]+\s*(\d+)", cuerpo, _re.IGNORECASE)
            return m.group(1) if m else None
        err = _c("ERRORES")
        mapeo["errores"] = err
        print(f"  [auto] RESUMEN -> errores: {err or '?'} | warnings: {_c('WARNINGS') or '?'} "
              f"| ok: {_c('OK') or '?'}")
        if err == "0":
            print("  >>> 0 ERRORES. Listo (el usuario pulsa 'Pasar borrador' / 'Pasar a calidad').")
        elif err is not None:
            print(f"  >>> {err} ERROR(ES): probablemente GEOMETRIA (terreno/construccion) o")
            print("  >>> ajuste del usuario. Revisa el Resumen.")
    except Exception:
        pass
    print("  (auto: NO pasa a calidad; geometria es reserva del usuario.)")
    return mapeo


def tramite_cancelacion(page, semilla: str = "") -> None:
    """Proceso COMPLETO de un tramite 'Cancelaciones - Fuerza Mayor' (3 pasos:
    Fuente Administrativa -> Resumen -> Borrador Resolucion).

    Paso 1: llena el 'Motivo de la cancelacion' (causa de fuerza mayor, texto variado y
    sintetico, no repetido) y la Fuente Administrativa (reutiliza fuente_administrativa).
    Luego avanza al Resumen y lee las validaciones. NO pasa a calidad (critico, lo
    confirma el usuario).

    Devuelve un dict con los datos usados (para el resumen.txt).
    """
    import random
    import re as _re
    rnd = random.Random(semilla + "-cancel") if semilla else random.Random()

    # Motivos de fuerza mayor (variados). Se arma con numeros/fechas ficticias.
    anio = rnd.randint(2023, 2026)
    mes = rnd.randint(1, 12)
    dia = rnd.randint(1, 28)
    fecha = f"{dia:02d}/{mes:02d}/{anio}"
    num_acta = rnd.randint(100, 999)
    plantillas = [
        (f"Predio afectado por fenomeno de remocion en masa que ocasiono el hundimiento "
         f"total y la falla geologica del terreno el {fecha}, imposibilitando su "
         f"existencia fisica, segun concepto tecnico de gestion del riesgo No. {num_acta}."),
        (f"Predio sumergido de forma permanente por desbordamiento y cambio de cauce del "
         f"rio el {fecha}, con perdida total por afectacion de ribera, segun informe "
         f"pericial de visita de campo No. {num_acta}."),
        (f"Desaparicion del terreno por socavacion y colapso de ladera por erosion severa "
         f"ocurrida el {fecha}, segun resolucion de declaratoria de calamidad publica "
         f"No. {num_acta}."),
        (f"Predio destruido por avenida torrencial e inundacion subita el {fecha}, que "
         f"dejo el lote sumergido de forma permanente, segun acta de gestion del riesgo "
         f"No. {num_acta}."),
    ]
    motivo = rnd.choice(plantillas)

    # 1) Motivo de la cancelacion (textarea obligatorio, el primero del formulario).
    try:
        ta = page.locator("textarea")
        if ta.count() > 0:
            ta.first.fill(motivo)
            ta.first.evaluate(
                "el => { el.dispatchEvent(new Event('input',{bubbles:true}));"
                " el.dispatchEvent(new Event('change',{bubbles:true})); }")
            print(f"  Motivo de la cancelacion: {motivo}")
        else:
            print("  [aviso] no se encontro el textarea del motivo de cancelacion.")
    except Exception as e:
        print(f"  [aviso] motivo de cancelacion: {type(e).__name__}")

    # 2) Fuente Administrativa (desplegables + numeros/fechas) -> reutiliza la funcion.
    try:
        fuente_administrativa(page, semilla)
    except Exception as e:
        print(f"  [aviso] fuente administrativa: {type(e).__name__}")

    page.wait_for_timeout(800)

    # 3) Avanzar al Resumen (este wizard es corto: Fuente -> Resumen).
    for _ in range(4):
        n = detectar_paso(page)
        # En este tipo el stepper tiene 3 pasos; 'detectar_paso' puede no mapearlo igual,
        # asi que avanzamos por el boton y nos detenemos al ver el Resumen.
        try:
            cuerpo = page.locator("body").inner_text()
        except Exception:
            cuerpo = ""
        if "Resumen Final" in cuerpo or "Validaciones del tr" in cuerpo:
            break
        continuar_wizard(page)
        page.wait_for_timeout(1300)

    # 4) Re-validar y leer conteo.
    try:
        rev = page.get_by_role("button", name="Re-validar")
        if rev.count() == 0:
            rev = page.locator("button", has_text="validar")
        if rev.count() > 0:
            rev.first.click()
            page.wait_for_timeout(2500)
            page.wait_for_load_state("networkidle")
    except Exception:
        pass
    errores = None
    try:
        cuerpo = page.locator("body").inner_text()
        def _conteo(etq):
            m = _re.search(r"(\d+)\s*[\r\n]+\s*" + etq, cuerpo, _re.IGNORECASE)
            return m.group(1) if m else None
        errores = _conteo("ERRORES")
        print(f"  VALIDACIONES -> errores: {errores or '?'} | "
              f"warnings: {_conteo('WARNINGS') or '?'} | ok: {_conteo('OK') or '?'}")
        if errores == "0":
            print("  >>> 0 ERRORES. Listo para 'Pasar borrador acto administrativo' y")
            print("  >>> 'Pasar a calidad' (ACCIONES CRITICAS, las confirma el usuario).")
        elif errores is not None:
            print(f"  >>> HAY {errores} ERROR(ES): revisar antes de calidad.")
    except Exception:
        pass
    print("  (El comando NO pasa a calidad automaticamente.)")
    return {"motivo": motivo, "errores": errores}


def tramite_propietario_completo(page, semilla: str = "", modo: str = "sustitucion",
                                copropietarios: int = 1, sexo: str = "") -> None:
    """Proceso COMPLETO de un Cambio de Propietario de corrido, asumiendo que ya se esta
    dentro del wizard en el Paso 2 (Propietario):

    1. Ejecuta el cambio de propietario (nuevo_propietario, modo indicado).
    2. Avanza paso a paso (Siguiente Paso / Continuar) hasta llegar al Resumen (paso 6/7).
       En pasos cartograficos (Terreno/Construccion) intenta continuar sin geometria
       (Cambio de Propietario no la exige). Si un paso bloquea, se detiene limpio.
    3. En el Resumen, dispara 'Re-validar' si existe y lee el conteo de validaciones.
    4. NO pulsa 'Pasar a calidad' (accion critica): se detiene e informa para que el
       usuario revise y confirme.
    """
    import re as _re
    # 1) Cambio de propietario en el Paso 2.
    nuevo_propietario(page, semilla, "100", modo, copropietarios, sexo)
    page.wait_for_timeout(1000)

    # 2) Avanzar por el wizard hasta el Resumen.
    ultimo = None
    estancado = 0
    for _ in range(14):
        n = detectar_paso(page)
        if n is None:
            break
        if n == ultimo:
            estancado += 1
        else:
            estancado = 0
        ultimo = n
        if n >= 6:  # Resumen (en Cambio de Propietario el Resumen suele ser el paso 6)
            break
        # Pasos alfanumericos que podemos completar en el camino.
        if n == 5:
            try:
                fuente_administrativa(page, semilla)
            except Exception:
                pass
        # Intentar avanzar.
        continuar_wizard(page)
        page.wait_for_timeout(1300)
        nuevo = detectar_paso(page)
        if nuevo == n:
            # No avanzo. Si es cartografico, se detiene (reserva usuario). Si no, reintenta.
            if estancado >= 2:
                print(f"  Detenido en Paso {n}: no avanza (posible geometria/validacion requerida).")
                return

    # 3) En el Resumen: re-validar y leer conteo.
    n = detectar_paso(page)
    print(f"  Paso actual tras avanzar: {n}")
    try:
        rev = page.get_by_role("button", name="Re-validar")
        if rev.count() == 0:
            rev = page.locator("button", has_text="validar")
        if rev.count() > 0:
            rev.first.click()
            page.wait_for_timeout(3000)
            page.wait_for_load_state("networkidle")
    except Exception:
        pass
    try:
        cuerpo = page.locator("body").inner_text()
        # El conteo viene como bloques: el numero y en la linea siguiente la etiqueta
        # (ERRORES / WARNINGS / OK / OMITIDAS). Capturamos 'N<sep>ETIQUETA'.
        def _conteo(etiqueta):
            m = _re.search(r"(\d+)\s*[\r\n]+\s*" + etiqueta, cuerpo, _re.IGNORECASE)
            if not m:
                m = _re.search(etiqueta + r"\s*[\r\n]+\s*(\d+)", cuerpo, _re.IGNORECASE)
            return m.group(1) if m else None
        errores = _conteo("ERRORES")
        warnings = _conteo("WARNINGS")
        ok = _conteo("OK")
        print(f"  VALIDACIONES -> errores: {errores or '?'} | "
              f"warnings: {warnings or '?'} | ok: {ok or '?'}")
        if errores == "0":
            print("  >>> 0 ERRORES. El tramite esta listo. Para cerrarlo: 'Pasar borrador")
            print("  >>> acto administrativo' y luego 'Pasar a calidad' (ACCIONES CRITICAS,")
            print("  >>> las confirma y pulsa el USUARIO).")
        elif errores is None:
            print("  >>> No se pudo leer el conteo con certeza. Revisa con 'cap'.")
        else:
            print(f"  >>> HAY {errores} ERROR(ES): corrige antes de pasar a calidad.")
    except Exception:
        print("  No se pudo leer el conteo de validaciones; revisa con 'cap'.")
    print("  (El comando NO pasa a calidad automaticamente. Revisa y confirma tu.)")


def llenar_construccion(page, anio: str = "", semilla: str = "") -> None:
    """Llena el modal 'Nueva unidad de construccion' (Paso 4) con datos sinteticos
    coherentes de una vivienda, incluida la CALIFICACION CATASTRAL completa.

    Requiere que la geometria (plantas) ya este cargada por el usuario. El comando:
      - Elige Tipo unidad = Residencial y Uso (primera opcion valida) si estan vacios.
      - Estado de conservacion = Bueno.
      - Año de construccion (parametro o aleatorio valido 1990-2020).
      - Baños/habitaciones/locales y observaciones.
      - Calificacion catastral: elige una opcion coherente (nivel medio) en cada uno de
        los 16 desplegables de calificacion.
      - Pulsa 'Agregar UC'.

    Mapa de <select> cuando el tipo de unidad ya esta elegido (19 en total):
      [0] Tipo unidad  [1] Uso  [2] Estado conservacion
      [3] Armazon [4] Muros [5] Cubierta [6] subtotal-estructura
      [7] Fachada [8] Cubrimiento muros [9] Piso [10] subtotal-acabados
      [11] Tamaño baño [12] Mobiliario baño [13] Enchape baño [14] subtotal-baño
      [15] Tamaño cocina [16] Mobiliario cocina [17] Enchape cocina [18] subtotal-cocina
    """
    import random
    if semilla:
        random.seed(semilla + "-uc")

    def sel_por_opcion(idx, contiene):
        """Elige en el select idx la primera opcion cuyo texto contenga 'contiene'."""
        selects = page.locator("select")
        if idx >= selects.count():
            return False
        opts = [selects.nth(idx).locator("option").nth(j).inner_text().strip()
                for j in range(selects.nth(idx).locator("option").count())]
        for t in opts:
            if contiene.lower() in t.lower():
                try:
                    selects.nth(idx).select_option(label=t)
                    return True
                except Exception:
                    return False
        return False

    def sel_primera_valida(idx):
        selects = page.locator("select")
        if idx >= selects.count():
            return False
        opts = [selects.nth(idx).locator("option").nth(j).inner_text().strip()
                for j in range(selects.nth(idx).locator("option").count())]
        for t in opts:
            tl = t.lower()
            if t and not tl.startswith("—") and "seleccione" not in tl and "sin selección" not in tl:
                try:
                    selects.nth(idx).select_option(label=t)
                    return True
                except Exception:
                    return False
        return False

    # 0) Tipo unidad y uso (si no estan elegidos).
    selects = page.locator("select")
    total = selects.count()
    if total < 3:
        print("  No parece el modal de construccion. ¿Esta abierto 'Nueva unidad de construccion'?")
        return
    # Tipo unidad (idx 0) -> Residencial.
    try:
        if selects.nth(0).input_value() in ("", None):
            sel_por_opcion(0, "Residencial")
            page.wait_for_timeout(700)
    except Exception:
        pass
    # Uso (idx 1): esperar a que carguen las opciones tras elegir el tipo, y elegir una
    # opcion real (no el placeholder 'Usos de ...'). Reintenta por timing.
    try:
        puesto_uso = False
        for _ in range(8):  # hasta ~4 s a que carguen los usos
            selects = page.locator("select")
            opts = [selects.nth(1).locator("option").nth(j).inner_text().strip()
                    for j in range(selects.nth(1).locator("option").count())]
            validas = [t for t in opts if t and "usos de" not in t.lower()
                       and "seleccione" not in t.lower() and "tipo de unidad" not in t.lower()]
            if validas:
                # Preferir un uso de vivienda coherente si existe.
                objetivo = None
                for pref in ("Vivienda hasta 3 pisos", "Apartamentos 4 y más pisos"):
                    if pref in validas:
                        objetivo = pref
                        break
                if objetivo is None:
                    objetivo = validas[0]
                selects.nth(1).select_option(label=objetivo)
                selects.nth(1).evaluate(
                    "el => { el.dispatchEvent(new Event('input',{bubbles:true}));"
                    " el.dispatchEvent(new Event('change',{bubbles:true})); }")
                print(f"  Uso = {objetivo!r}")
                puesto_uso = True
                break
            page.wait_for_timeout(500)
        if not puesto_uso:
            print("  [aviso] no se pudo fijar el Uso (opciones no cargaron).")
        page.wait_for_timeout(900)
    except Exception as e:
        print(f"  [aviso] Uso: {type(e).__name__}")

    # Estado de conservacion (idx 2) -> Bueno.
    sel_por_opcion(2, "Bueno")

    # Año de construccion (obligatorio). El input del año es el unico con min=1800
    # (max=2026). Puede venir con value='0', por eso NO basta buscar 'vacio'.
    anio = (anio or "").strip() or str(random.randint(1990, 2020))
    puesto = False
    try:
        inp = page.locator("input[min='1800']")
        if inp.count() > 0:
            inp.first.fill(anio)
            inp.first.evaluate(
                "el => { el.dispatchEvent(new Event('input',{bubbles:true}));"
                " el.dispatchEvent(new Event('change',{bubbles:true})); }")
            puesto = True
    except Exception:
        pass
    if not puesto:
        # Respaldo: input number con value 0 o vacio (evitando readonly).
        try:
            inp = page.locator("input[type='number']:not([readonly])")
            for i in range(inp.count()):
                v = inp.nth(i).input_value()
                if v in ("", "0", None):
                    inp.nth(i).fill(anio)
                    puesto = True
                    break
        except Exception:
            pass
    print(f"  Año construccion = {anio}" + ("" if puesto else " [aviso: no se pudo fijar]"))

    # Calificacion catastral: perfil CONSERVADOR (sencillo/regular), coherente con una
    # vivienda estandar. NO calificar alto (eso subiria el avaluo y perjudicaria al
    # propietario). Se eligen opciones de bajo-medio puntaje; los subtotales
    # (Malo/Regular/Bueno/Excelente) se dejan en 'Regular'.
    selects = page.locator("select")
    n = selects.count()
    # Preferencias por indice. Perfil CONSERVADOR con VARIACION: por cada campo hay
    # varias opciones de bajo-medio puntaje y se elige una al azar (semilla por tramite),
    # de modo que la calificacion sea conservadora pero DIFERENTE entre tramites.
    opciones_conservadoras = {
        3: ["Ladrillo, bloque", "Prefabricado", "Concreto hasta tres pisos"],  # Armazon
        4: ["Bahareque, adobe, tapia", "Madera", "Concreto prefabricado"],     # Muros
        5: ["Zinc, teja de barro", "Eternit o teja de barro", "Materiales de desecho"],  # Cubierta
        6: ["Regular", "Bueno"],                                               # subtotal
        7: ["Pobre", "Sencilla", "Regular"],                                   # Fachada
        8: ["Sin cubrimiento", "Pañete", "Estuco"],                            # Cubrim. muros
        9: ["Tierra pisada", "Cemento, madera burda", "Baldosa común"],        # Piso
        10: ["Regular", "Bueno"],                                              # subtotal
        11: ["Pequeño", "Mediano"],                                            # Tamaño baño
        12: ["Pobre", "Sencillo", "Regular"],                                  # Mobiliario baño
        13: ["Sin cubrimiento", "Pañete, baldosa común", "Baldosín unicolor"], # Enchape baño
        14: ["Regular", "Bueno"],                                             # subtotal
        15: ["Pequeña", "Mediana"],                                           # Tamaño cocina
        16: ["Pobre", "Sencillo", "Regular"],                                 # Mobiliario cocina
        17: ["Sin cubrimiento", "Pañete, baldosa", "Baldosín unicolor"],      # Enchape cocina
        18: ["Regular", "Bueno"],                                             # subtotal
    }
    preferencias = {idx: random.choice(ops) for idx, ops in opciones_conservadoras.items()}
    hechos = 0
    for idx in range(3, min(n, 19)):
        pref = preferencias.get(idx)
        ok = False
        if pref:
            ok = sel_por_opcion(idx, pref)
        if not ok:
            ok = sel_primera_valida(idx)
        if ok:
            hechos += 1
    print(f"  Calificacion catastral: {hechos} desplegables llenados.")

    # Total baños / habitaciones / locales: valores coherentes de vivienda (variados,
    # no repetidos). Son inputs number con min=0 (los 3 editables, no readonly).
    banos = random.randint(1, 3)
    habitaciones = random.randint(2, 5)
    locales = 0  # vivienda residencial: sin locales
    try:
        inp0 = page.locator("input[type='number'][min='0']:not([readonly])")
        # Orden esperado: [0]=Total baños, [1]=Total habitaciones, [2]=Total locales.
        if inp0.count() >= 1:
            inp0.nth(0).fill(str(banos))
        if inp0.count() >= 2:
            inp0.nth(1).fill(str(habitaciones))
        if inp0.count() >= 3:
            inp0.nth(2).fill(str(locales))
        print(f"  Total baños={banos} | habitaciones={habitaciones} | locales={locales}")
    except Exception as e:
        print(f"  [aviso] baños/habitaciones/locales: {type(e).__name__}")

    # Observaciones.
    try:
        tas = page.locator("textarea")
        for i in range(tas.count()):
            if tas.nth(i).input_value() in ("", None):
                tas.nth(i).fill("sin observacion")
        print("  Observaciones = 'sin observacion'")
    except Exception:
        pass

    print("  Construccion lista para 'Agregar UC'. Revisa y pulsa Agregar (o usa click).")


def cambiar_destino(page, destino: str = "Habitacional") -> None:
    """Cambia el 'Destino Económico' del predio (Paso 1) al valor indicado.

    Regla: en tramites con construccion (p. ej. Mutacion 3a - Cambio Area Construida)
    el destino NO debe quedar como 'Lote ... No Construido'; debe ser coherente con un
    predio edificado (Habitacional por defecto; tambien Comercial, Industrial, etc.).

    Localiza el <select> de destino por sus opciones caracteristicas (contiene
    'Habitacional' y 'Comercial'), no por indice.
    """
    destino = (destino or "Habitacional").strip()
    selects = page.locator("select")
    sel_destino = None
    for i in range(selects.count()):
        try:
            opts = [selects.nth(i).locator("option").nth(j).inner_text().strip()
                    for j in range(selects.nth(i).locator("option").count())]
        except Exception:
            continue
        if "Habitacional" in opts and "Comercial" in opts:
            sel_destino = selects.nth(i)
            opciones = opts
            break
    if sel_destino is None:
        print("  No se encontro el desplegable de Destino Económico.")
        return
    # Coincidencia exacta o por prefijo (tolerante a tildes/variaciones simples).
    objetivo = None
    for t in opciones:
        if t.lower() == destino.lower() or t.lower().startswith(destino.lower()):
            objetivo = t
            break
    if objetivo is None:
        print(f"  '{destino}' no esta entre las opciones de Destino. Opciones: {opciones[:8]}...")
        return
    try:
        sel_destino.select_option(label=objetivo)
        page.wait_for_timeout(400)
        print(f"  Destino Económico = {objetivo!r}")
    except Exception as e:
        print(f"  No se pudo cambiar el destino: {type(e).__name__}: {e}")


def caracterizacion_ladm(page, tipo_predio: str = "Privado",
                         tipo_derecho: str = "Dominio") -> None:
    """Llena la 'Caracterizacion LADM del Predio' (Paso 1): Tipo de Predio y
    Tipo de Derecho. La Condicion suele ser readonly (derivada del NPN).

    Localiza los desplegables por sus opciones caracteristicas, no por indice, para
    ser robusto si hay otros <select> en la pagina.
    """
    selects = page.locator("select")
    total = selects.count()
    if total == 0:
        print("  No hay desplegables. ¿Estas en el Paso 1 (Caracterizacion LADM)?")
        return

    def opciones(i):
        o = selects.nth(i).locator("option")
        return [o.nth(j).inner_text().strip() for j in range(o.count())]

    sel_predio = sel_derecho = None
    for i in range(total):
        txt = opciones(i)
        joined = " ".join(txt)
        if "Privado" in txt and ("Baldío" in joined or "Baldio" in joined):
            sel_predio = selects.nth(i)
        if "Dominio" in txt and ("Usufructo" in txt or "Nuda Propiedad" in txt):
            sel_derecho = selects.nth(i)

    hechos = 0
    if sel_predio is not None:
        try:
            sel_predio.select_option(label=tipo_predio)
            print(f"  Tipo de Predio = {tipo_predio!r}")
            hechos += 1
        except Exception as e:
            print(f"  No se pudo elegir Tipo de Predio: {type(e).__name__}")
    else:
        print("  No se encontro el desplegable de Tipo de Predio.")
    if sel_derecho is not None:
        try:
            sel_derecho.select_option(label=tipo_derecho)
            print(f"  Tipo de Derecho = {tipo_derecho!r}")
            hechos += 1
        except Exception as e:
            print(f"  No se pudo elegir Tipo de Derecho: {type(e).__name__}")
    else:
        print("  No se encontro el desplegable de Tipo de Derecho.")
    page.wait_for_timeout(400)
    print(f"  Caracterizacion LADM: {hechos}/2 campos llenados.")


def calcular_avaluo(page, anio: str) -> None:
    """Automatiza el Paso 6 (Avaluo): elige la vigencia del retroactivo y pulsa
    'Calcular retroactivo'.

    Mapa (confirmado en R-2026-0057):
      - Desplegable 'Vigencia' del bloque AVALUO RETROACTIVO (unico <select> del paso).
      - Boton 'Calcular retroactivo'.
    Al elegir el año N se calculan/guardan las vigencias desde N hasta la anterior a
    la actual.
    """
    anio = (anio or "").strip()
    if not anio:
        print("  Uso: avaluo <anio>  (p. ej. avaluo 2025)")
        return
    # Seleccionar la vigencia. En este paso suele haber un unico <select>.
    selects = page.locator("select")
    if selects.count() == 0:
        print("  No hay desplegable de vigencia. ¿Estas en el Paso 6 (Avaluo)?")
        return
    # Si hay varios, tomar el que tenga el año como opcion.
    objetivo = None
    for i in range(selects.count()):
        opts = selects.nth(i).locator("option")
        textos = [opts.nth(j).inner_text().strip() for j in range(opts.count())]
        if anio in textos:
            objetivo = selects.nth(i)
            break
    if objetivo is None:
        objetivo = selects.first
    try:
        objetivo.select_option(label=anio)
        print(f"  Vigencia seleccionada: {anio}")
    except Exception as e:
        print(f"  No se pudo seleccionar la vigencia {anio}: {type(e).__name__}: {e}")
        return
    page.wait_for_timeout(500)
    # Pulsar 'Calcular retroactivo'.
    boton = page.get_by_role("button", name="Calcular retroactivo")
    if boton.count() == 0:
        boton = page.locator("button", has_text="Calcular retroactivo")
    if boton.count() == 0:
        print("  No se encontro el boton 'Calcular retroactivo'.")
        return
    boton.first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")
    print(f"  Avaluo retroactivo calculado desde {anio}. Revisa la tabla de vigencias.")


def fuente_administrativa(page, semilla: str = "") -> None:
    """Rellena en bloque el Paso 5 (Fuente Administrativa) con datos sinteticos.

    Mapa del formulario (confirmado en R-2026-0057, Efectos Registrales):
      Desplegables (en orden en la pagina):
        [0] Tipo de Fuente       -> Escritura Pública
        [1] Estado Disponibilidad-> Disponible
        [2] Adquisicion          -> A-Tradicion
        [3] Ente Emisor          -> Notaria
        [4] Departamento Origen  -> Valle del Cauca
        [5] Municipio Origen     -> Jamundi (se habilita tras elegir depto)
        [6] Naturaleza Juridica  -> una opcion valida
      Texto:
        input[placeholder='Ej: 1234'] -> Numero de Escritura/Documento
        input[placeholder='Ej: 5']    -> Oficina de Origen
      Fecha:
        input[type=date] nth=0 -> Fecha Documento Fuente
        input[type=date] nth=1 -> Fecha de Anotacion (si existe)

    Los valores variables (numero de escritura, oficina, fechas, anotacion) se
    generan aleatorios para NO repetir entre tramites. 'semilla' permite fijar la
    aleatoriedad por radicado si se desea reproducibilidad.
    """
    import random
    if semilla:
        random.seed(semilla)

    # Valores de desplegables (por etiqueta). Si alguno no existe, se informa.
    desplegables = [
        ("Tipo de Fuente", "Escritura Pública"),
        ("Estado de Disponibilidad", "Disponible"),
        ("Adquisicion", "A-Tradicion"),
        ("Ente Emisor", "Notaria"),
        ("Departamento de Origen", "Valle del Cauca"),
        ("Municipio de Origen", None),   # se resuelve por coincidencia 'Jamund'
        ("Naturaleza Juridica", None),   # se elige la primera opcion real valida
    ]

    selects = page.locator("select")
    total = selects.count()
    if total < 7:
        print(f"  Solo hay {total} desplegables; ¿estas en el Paso 5 (Fuente Administrativa)?")
        return
    # Esperar a que los desplegables terminen de poblar sus opciones (carga async).
    # Sin esto, si se corre muy rapido, los <option> aun no existen y no se llena nada.
    for _ in range(20):  # hasta ~6 s
        try:
            op0 = selects.nth(0).locator("option").count()
            op2 = selects.nth(2).locator("option").count()
            if op0 >= 2 and op2 >= 2:
                break
        except Exception:
            pass
        page.wait_for_timeout(300)

    def _es_placeholder(t: str) -> bool:
        tl = t.lower()
        return (tl == "" or tl.startswith("seleccione") or tl.startswith("selecione")
                or tl.startswith("—") or t.strip() == "—")

    def elegir(idx: int, etiqueta: str | None, contiene: str | None = None):
        sel = selects.nth(idx)
        opciones = sel.locator("option")
        n = opciones.count()
        textos = [opciones.nth(j).inner_text().strip() for j in range(n)]
        objetivo = None
        # 1) Coincidencia exacta o por prefijo con la etiqueta preferida.
        if etiqueta:
            for t in textos:
                if t == etiqueta or t.startswith(etiqueta):
                    objetivo = t
                    break
        # 2) Coincidencia por 'contiene'.
        if objetivo is None and contiene:
            for t in textos:
                if contiene.lower() in t.lower():
                    objetivo = t
                    break
        # 3) FALLBACK ROBUSTO: primera opcion valida (no placeholder).
        if objetivo is None:
            for t in textos:
                if not _es_placeholder(t):
                    objetivo = t
                    break
        if objetivo is None:
            print(f"    [select {idx}] sin opcion valida (solo placeholder).")
            return False
        # Intento por etiqueta y, si falla, por indice de la opcion elegida.
        try:
            sel.select_option(label=objetivo)
            print(f"    [select {idx}] = {objetivo!r}")
            return True
        except Exception:
            try:
                idx_op = textos.index(objetivo)
                sel.select_option(index=idx_op)
                print(f"    [select {idx}] = {objetivo!r} (por indice)")
                return True
            except Exception as e:
                print(f"    [select {idx}] error: {type(e).__name__}")
                return False

    print("  Llenando Fuente Administrativa (Paso 5) con datos sinteticos...")
    _ok = 0
    _ok += 1 if elegir(0, "Escritura Pública") else 0
    _ok += 1 if elegir(1, "Disponible") else 0
    _ok += 1 if elegir(2, "A-Tradicion") else 0
    _ok += 1 if elegir(3, "Notaria") else 0
    _ok += 1 if elegir(4, "Valle del Cauca") else 0
    page.wait_for_timeout(900)  # dar tiempo a que cargue el municipio
    _ok += 1 if elegir(5, None, contiene="Jamund") else 0
    _ok += 1 if elegir(6, None) else 0  # primera naturaleza juridica valida

    # Campos de texto variables (unicos por tramite).
    num_escritura = str(random.randint(1000, 9999))
    oficina = str(random.randint(1, 12))
    try:
        caja = page.locator("input[placeholder='Ej: 1234']")
        if caja.count() > 0:
            caja.first.fill(num_escritura)
            print(f"    Numero de Escritura/Documento = {num_escritura}")
    except Exception:
        pass
    try:
        caja = page.locator("input[placeholder='Ej: 5']")
        if caja.count() > 0:
            caja.first.fill(oficina)
            print(f"    Oficina de Origen = {oficina}")
    except Exception:
        pass

    # Fechas (coherentes: documento antes que anotacion, ambas en el pasado).
    anio = random.randint(2008, 2020)
    mes = random.randint(1, 12)
    dia = random.randint(1, 28)
    fecha_doc = f"{anio:04d}-{mes:02d}-{dia:02d}"
    # Anotacion unos dias despues.
    dia2 = min(dia + random.randint(3, 20), 28)
    fecha_anot = f"{anio:04d}-{mes:02d}-{dia2:02d}"
    fechas = page.locator("input[type=date]")
    try:
        if fechas.count() > 0:
            fechas.nth(0).fill(fecha_doc)
            print(f"    Fecha Documento Fuente = {fecha_doc}")
        if fechas.count() > 1:
            fechas.nth(1).fill(fecha_anot)
            print(f"    Fecha de Anotacion = {fecha_anot}")
    except Exception:
        pass

    # Anotacion: campo de texto (input con placeholder de anotacion si existe).
    anotacion = f"{random.randint(1, 500):04d}"
    try:
        caja = page.locator("input[placeholder*='anotación'], input[placeholder*='anotacion']")
        if caja.count() > 0:
            caja.first.fill(anotacion)
            print(f"    Anotacion (Nro) = {anotacion}")
    except Exception:
        pass

    # Observacion: el/los textarea del formulario -> 'sin observacion'.
    try:
        tas = page.locator("textarea")
        escritos = 0
        for i in range(tas.count()):
            t = tas.nth(i)
            try:
                if t.input_value() in ("", None):
                    t.fill("sin observacion")
                    escritos += 1
            except Exception:
                continue
        if escritos:
            print(f"    Observacion (textarea x{escritos}) = 'sin observacion'")
    except Exception:
        pass

    print(f"  Paso 5 rellenado ({_ok}/7 desplegables). Revisa en pantalla y avanza con 'continuar'.")
    return _ok


def diagnosticar_paso(page) -> None:
    """Informa en que paso del wizard estamos y si es automatizable o manual.

    Si el paso requiere intervencion del usuario (cartografico), lo indica con la
    frase de pausa acordada para que el usuario actue y luego diga 'listo'.
    """
    n = detectar_paso(page)
    if n is None:
        print("  No se pudo determinar el paso activo del wizard.")
        print("  Sugerencia: usa 'cap' y revisa la pantalla, o verifica que estas en /gestion-tramites.")
        return
    info = WIZARD_PASOS.get(n, {})
    nombre = info.get("nombre", "?")
    naturaleza = info.get("naturaleza", "?")
    detalle = info.get("detalle", "")
    # Detectar "solo lectura" en el cuerpo del paso actual.
    try:
        cuerpo = page.locator("body").inner_text().lower()
    except Exception:
        cuerpo = ""
    solo_lectura = "solo lectura" in cuerpo

    print(f"  === PASO {n}: {nombre} ===")
    print(f"  {detalle}")
    if naturaleza == "manual":
        print("")
        print(f"  >>> ACCION DEL USUARIO REQUERIDA (paso cartografico/manual).")
        print(f"  >>> Paso cartografico alcanzado en el tramite. Queda en espera de tu")
        print(f"  >>> intervencion manual sobre {nombre.lower()}.")
        print(f"  >>> Cuando termines, escribe 'listo' o 'continuar' para seguir.")
    else:
        if solo_lectura:
            print("  -> Paso de SOLO LECTURA: no hay campos que editar. Se avanza con 'continuar'.")
        else:
            print("  -> Paso AUTOMATIZABLE (alfanumerico): el agente provee los datos a llenar.")
    print(f"  (naturaleza: {naturaleza}{' | solo lectura detectado' if solo_lectura else ''})")


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
    # El nombre del boton cambia por paso: 'Continuar' (1), 'Siguiente Paso' (2-4),
    # 'Siguiente: Resumen Final' (paso 4 Construccion -> Resumen), 'Pasar borrador...'.
    for nombre in ("Siguiente: Resumen Final", "Siguiente Paso", "Continuar"):
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
        print("  No se encontro el boton de avanzar (Continuar / Siguiente Paso / Resumen).")
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


def entrar_radicado(page, base_url: str, radicado: str) -> bool:
    """Secuencia COMPLETA para entrar directo al wizard de un radicado:
    Asignacion -> filtrar Asignado -> buscar por el buscador -> abrir detalle ->
    pulsar 'Iniciar Tramite'. Deja la pagina en el wizard (/gestion-tramites).

    Util para revisar cada radicado sin encadenar comandos a mano.
    """
    print(f"  [1/4] Navegando a Asignacion y filtrando Asignado...")
    ir_asignacion(page, base_url)
    filtrar_estado(page, "Asignado")
    print(f"  [2/4] Buscando {radicado} por el buscador...")
    buscador = page.locator("input[placeholder*='Buscar por radicado']")
    if buscador.count() > 0:
        buscador.first.fill("")
        buscador.first.type(radicado, delay=15)
        page.wait_for_timeout(1500)
        page.wait_for_load_state("networkidle")
    print(f"  [3/4] Abriendo detalle de {radicado}...")
    if not abrir_detalle(page, radicado):
        print(f"  No se pudo abrir el detalle de {radicado}.")
        return False
    page.wait_for_timeout(800)
    print(f"  [4/4] Pulsando 'Iniciar Tramite'...")
    boton = page.get_by_role("button", name="Iniciar Trámite")
    if boton.count() == 0:
        boton = page.get_by_text("Iniciar Trámite", exact=False)
    if boton.count() == 0:
        print("  No hay boton 'Iniciar Tramite' (quiza requiere Asignacion de NPN, o ya iniciado).")
        return False
    boton.first.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)
    print("  Dentro del wizard. Usa 'paso' para ver en que paso estas.")
    mostrar_estado(page)
    return True


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
            elif cmd == "entrar":
                if not arg:
                    print("  Uso: entrar <numero de radicado>")
                else:
                    entrar_radicado(page, base_url, arg)
            elif cmd == "predio":
                # Uso: predio <NPN o numero de predio> -> selecciona la tarjeta del
                # LISTADO DE PREDIOS (clica el <button>, no el desplegable de copiar).
                if not arg:
                    print("  Uso: predio <NPN o numero de predio>  (p. ej. predio 112071)")
                else:
                    seleccionar_predio(page, arg)
            elif cmd == "siguiente":
                siguiente_radicado(page, base_url)
            elif cmd == "iniciar":
                iniciar_tramite(page)
            elif cmd == "validar":
                if not arg:
                    print("  Uso: validar <numero de radicado>")
                else:
                    validar_radicado(page, base_url, arg)
            elif cmd == "listar":
                listar_todas_paginas(page, base_url)
            elif cmd == "agregarfoto":
                agregar_foto(page)
            elif cmd == "subirfoto":
                if not arg:
                    print("  Uso: subirfoto <ruta del archivo de imagen>")
                else:
                    subir_foto(page, arg)
            elif cmd == "continuar":
                continuar_wizard(page)
            elif cmd == "paso":
                diagnosticar_paso(page)
            elif cmd == "puntosmasivo":
                # Uso: puntosmasivo <TipoPunto> | <Metodo> | <PuntoControl>
                p1, _, resto = arg.partition("|")
                p2, _, p3 = resto.partition("|")
                tp = p1.strip() or "Mojón"
                me = p2.strip() or "Método Directo"
                pc = p3.strip() or "Apoyo"
                puntos_masivo(page, tp, me, pc)
            elif cmd == "linderosmasivo":
                # Uso: linderosmasivo <ruta del geojson del poligono>
                if not arg:
                    print("  Uso: linderosmasivo <ruta del .geojson del predio>")
                    print("  Ej: linderosmasivo C:\\...\\763640002000000030239000000000.geojson")
                else:
                    linderos_masivo(page, arg)
            elif cmd == "fuenteadmin":
                # Uso: fuenteadmin [semilla]  (semilla opcional, p.ej. el radicado)
                fuente_administrativa(page, arg.strip())
            elif cmd == "avaluo":
                # Uso: avaluo <anio>  (p. ej. avaluo 2025)
                calcular_avaluo(page, arg.strip())
            elif cmd == "caracterizacion":
                # Uso: caracterizacion [TipoPredio] | [TipoDerecho]
                p1, _, p2 = arg.partition("|")
                tp = p1.strip() or "Privado"
                td = p2.strip() or "Dominio"
                caracterizacion_ladm(page, tp, td)
            elif cmd == "editardireccion":
                # Uso: editardireccion [semilla]  -> estructura y llena la direccion
                editar_direccion(page, arg.strip())
            elif cmd == "destino":
                # Uso: destino [valor]  (def. Habitacional)
                cambiar_destino(page, arg.strip() or "Habitacional")
            elif cmd == "construccion":
                # Uso: construccion [anio] [semilla]
                partes_c = arg.split()
                anio_c = partes_c[0] if partes_c else ""
                sem_c = partes_c[1] if len(partes_c) > 1 else ""
                llenar_construccion(page, anio_c, sem_c)
            elif cmd == "propietario":
                # Uso: propietario [semilla] [modo] [n] [sexo]
                #   modo: sustitucion (def) | copropiedad
                #   n: nº de copropietarios (solo copropiedad). Ej: propietario R-0081 copropiedad 2
                #   sexo: femenino | masculino (opcional; def. aleatorio)
                partes_p = arg.split()
                sem_p = partes_p[0] if partes_p else ""
                modo_p = partes_p[1] if len(partes_p) > 1 else "sustitucion"
                n_p = int(partes_p[2]) if len(partes_p) > 2 and partes_p[2].isdigit() else 1
                sexo_p = ""
                for _t in partes_p[1:]:
                    if _t.lower() in ("femenino", "f", "mujer", "masculino", "m", "hombre"):
                        sexo_p = _t.lower()
                        break
                nuevo_propietario(page, sem_p, "100", modo_p, n_p, sexo_p)
            elif cmd == "autopaso":
                # Inspeccion dinamica del paso actual: llena editables, registra bloqueados.
                autopaso(page, arg.strip())
            elif cmd == "tramiteauto":
                # Uso: tramiteauto [semilla] [anio] [destino...]
                #   -> motor auto-adaptativo hasta Resumen. 'destino' opcional (varias
                #      palabras); si se omite, usa 'Lote Urbanizado No Construido' (lote).
                partes_a = arg.split()
                sem_a = partes_a[0] if partes_a else ""
                anio_a = partes_a[1] if len(partes_a) > 1 else "2025"
                destino_a = " ".join(partes_a[2:]) if len(partes_a) > 2 else ""
                tramite_auto(page, sem_a, anio_a, destino_a)
            elif cmd == "cancelacion":
                # Uso: cancelacion [semilla]  -> Cancelaciones - Fuerza Mayor completo
                tramite_cancelacion(page, arg.strip())
            elif cmd == "tramite3a":
                # Uso: tramite3a [semilla] [destino]  -> Mutacion 3a PARTE 1 (hasta Paso 4,
                # donde el usuario sube la geometria de la construccion).
                partes_3 = arg.split()
                sem_3 = partes_3[0] if partes_3 else ""
                dest_3 = " ".join(partes_3[1:]) if len(partes_3) > 1 else ""
                tramite3a_completo(page, sem_3, dest_3)
            elif cmd == "tramite3afin":
                # Uso: tramite3afin [semilla] [anio]  -> Mutacion 3a PARTE 2 (tras cargar
                # la geometria de la construccion): edita calificacion UC + avaluo + resumen.
                partes_3f = arg.split()
                sem_3f = partes_3f[0] if partes_3f else ""
                anio_3f = partes_3f[1] if len(partes_3f) > 1 else "2025"
                tramite3a_fin(page, sem_3f, anio_3f)
            elif cmd == "tramitepropietario":
                # Uso: tramitepropietario [semilla] [modo] [n] [sexo]
                #   -> cambio de propietario + avanza hasta el Resumen y valida (NO pasa
                #      a calidad). sexo: femenino | masculino (opcional; def. aleatorio).
                partes_tp = arg.split()
                sem_tp = partes_tp[0] if partes_tp else ""
                modo_tp = partes_tp[1] if len(partes_tp) > 1 else "sustitucion"
                n_tp = int(partes_tp[2]) if len(partes_tp) > 2 and partes_tp[2].isdigit() else 1
                sexo_tp = ""
                for _t in partes_tp[1:]:
                    if _t.lower() in ("femenino", "f", "mujer", "masculino", "m", "hombre"):
                        sexo_tp = _t.lower()
                        break
                tramite_propietario_completo(page, sem_tp, modo_tp, n_tp, sexo_tp)
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
