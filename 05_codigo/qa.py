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
    if semilla:
        random.seed(semilla + "-dir")

    # 1) Abrir el modal de editar si no esta abierto (busca el titulo 'Editar dirección').
    try:
        titulo = page.get_by_text("Editar dirección", exact=False)
        if titulo.count() == 0:
            # Intentar abrir con el icono de editar de la primera fila.
            lapiz = page.get_by_text("edit", exact=True)
            if lapiz.count() > 0:
                lapiz.first.click()
                page.wait_for_timeout(800)
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

    # Valores numericos coherentes y unicos.
    vp_valor = str(random.randint(1, 120))
    vp_letra = random.choice(["", "A", "B", "C"])
    vg_valor = str(random.randint(1, 90))
    vg_letra = random.choice(["", "A", "B"])
    num_predio = str(random.randint(1, 99))
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

    # 5) Pulsar 'Actualizar'.
    boton = page.get_by_role("button", name="Actualizar")
    if boton.count() == 0:
        boton = page.locator("button", has_text="Actualizar")
    if boton.count() > 0:
        boton.first.click()
        page.wait_for_timeout(1200)
        page.wait_for_load_state("networkidle")
        print(f"  Direccion estructurada ACTUALIZADA: {clase} {vp_valor}{vp_letra} "
              f"# {vg_valor}{vg_letra} - {num_predio}, CP {cod_postal}")
    else:
        print("  No se encontro el boton 'Actualizar'. Revisa el modal.")


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
