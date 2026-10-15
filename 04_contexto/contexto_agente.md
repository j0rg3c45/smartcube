# Contexto del Agente — Proyecto Catastral SmartCube

> Este documento es la fuente principal de contexto para el agente de IA.
> Debe leerse al inicio de cada sesión para entender el proyecto, su estructura
> y las convenciones de trabajo.

---

## 1. Descripción general

**SmartCube** es un proyecto **catastral** desarrollado para la empresa **SmartCube**.
El trabajo se apoya en **QGIS** para la gestión, edición y análisis de información
geográfica catastral, junto con herramientas propias y la tramitación de expedientes.

- **Dominio:** Catastro / Sistemas de Información Geográfica (SIG)
- **Herramienta principal:** QGIS
- **Empresa:** SmartCube
- **Repositorio:** https://github.com/j0rg3c45/smartcube.git
- **Plataforma de trabajo:** https://jamundi-dev.smartcubescol.com/ (entorno de desarrollo)

---

## 2. Estructura del proyecto

```
Smartcube/
├── 01_trabajos_qgis/     # Proyectos QGIS (.qgz) con el trabajo catastral
│   └── 01.trabajo_14102026.qgz
├── 02_herramientas_qgis/ # Herramientas / plugins de QGIS
│   └── smartcube_core.zip
├── 03_tramites/          # Expedientes y trámites catastrales
│   └── 01_tramite_/
│       └── 01_foto.png
├── 04_contexto/          # Documentación de contexto para el agente (esta carpeta)
│   └── contexto_agente.md
└── 05_codigo/            # Código fuente del proyecto (scripts, plugins, etc.)
```

### Rol de cada carpeta

| Carpeta | Contenido | Uso |
|---------|-----------|-----|
| `01_trabajos_qgis` | Proyectos QGIS (`.qgz`) | Trabajo cartográfico y catastral activo |
| `02_herramientas_qgis` | `smartcube_core.zip` (plugin existente) | Referencia. **NO se usa** en este proyecto |
| `03_tramites` | Expedientes de trámites | Documentación y evidencias (fotos, datos) por trámite |
| `04_contexto` | Documentación de contexto | **Fuente de contexto del agente** |
| `05_codigo` | Código fuente | **Todos los scripts y `.py`** del proyecto (PyQGIS / Python) |

---

## 3. Repositorio

- **URL:** https://github.com/j0rg3c45/smartcube.git
- **Uso:** aquí se sube (publica) el trabajo y el código del proyecto.
- **Flujo recomendado:**
  - Trabajar en ramas y abrir Pull Requests en lugar de empujar directo a `main`.
  - Mensajes de commit claros y en español.
  - Evitar subir archivos pesados o sensibles (p. ej. datos de trámites, fotos)
    salvo que se decida explícitamente; usar `.gitignore` cuando aplique.

---

## 4. Objetivo del agente

**Objetivo principal: pruebas (QA / testing) de la plataforma catastral SmartCube.**
Diseñar y ejecutar casos de prueba sobre la plataforma, detectar inconsistencias y
documentarlas, trabajando radicado por radicado hasta la meta de 50 (ver sección 8).

Apoyo al proceso de QA:
- Guiar paso a paso la navegación y validación en la plataforma.
- Escribir código de automatización/análisis en `05_codigo` cuando aporte (p. ej. Playwright, procesado de datos).
- Registrar y organizar las inconsistencias para el informe final.

### Guía de áreas críticas a evaluar (plan de pruebas)

**1. Módulos y funcionalidades clave**

- **Gestión de predios / componente alfanumérico:**
  - Altas, bajas y modificaciones: registro de predios, segregaciones (divisiones),
    englobes (uniones), cambios de propietario.
  - Reglas de negocio: que los identificadores prediales (NPN, códigos catastrales
    anteriores y nuevos) cumplan la estructura oficial de la normativa vigente.
  - Avalúos y destino económico: cálculos automáticos de avalúos, fórmulas según tipo
    de construcción, terreno y destino económico (residencial, comercial, rural, etc.).

- **Componente geográfico / SIG (GIS):**
  - Edición espacial: creación y edición de polígonos de terreno y construcciones.
  - Reglas topológicas: que el sistema impida o alerte sobre solapes (overlaps),
    huecos no permitidos (gaps) y geometrías inválidas.
  - Vinculación alfanumérica-espacial: que cada polígono corresponda a un único
    registro predial y que los cambios en uno se reflejen en el otro.

- **Trámites y conservación catastral:**
  - Flujo de trabajo (workflow): ciclo de vida de la solicitud (radicación, asignación
    a técnico/perito, revisión jurídica, aprobación y liquidación).
  - Trazabilidad y auditoría: registro de fecha, hora y usuario en cada modificación
    de datos o geometrías.

- **Interoperabilidad y salidas:**
  - Cargue y descargue masivo: importación/exportación de capas (Shapefile, GeoJSON,
    GDB, DXF) y tablas masivas (Excel, CSV).
  - Certificados y reportes: generación de cédulas catastrales, fichas prediales en PDF
    y resoluciones administrativas.

**2. Tipos de prueba recomendados**

- **Funcionales:** que cada botón, formulario, cálculo y flujo cumpla las
  especificaciones técnicas y legales.
- **Carga y rendimiento:** comportamiento del visor geográfico y de la base de datos
  con miles de predios o múltiples usuarios concurrentes.

---

## 5. Tecnologías y entorno

<!-- Completar / ajustar según corresponda -->
- **QGIS** (proyectos `.qgz`)
- **Python / PyQGIS** (pendiente de confirmar)
- **uv** como gestor de paquetes/entornos de Python.
  - Versión: `uv 0.11.11`
  - Ruta (instalación única del PC): `C:\Users\Jorge\.local\bin\uv.exe`
- **Sistema operativo:** Windows

### Plataforma SmartCube
- **Nombre:** "Jamundí — Sistema de Gestión Catastral".
- **URL (dev):** https://jamundi-dev.smartcubescol.com/
- **Tipo:** aplicación web de una sola página (SPA), el contenido se renderiza
  con JavaScript en el navegador (no viene en el HTML inicial).
- **Stack frontend (observado):**
  - Build con **Vite** (assets tipo `/assets/index-<hash>.js` y `.css`).
  - Fuentes **Inter** e iconos **Material Symbols** (Google Fonts).
  - Editor de texto enriquecido **CKEditor 5** en la interfaz.
- **Credenciales:** NO se guardan en el repositorio. Están en `05_codigo/.env`
  (ignorado por Git), con las variables `SMARTCUBE_URL`, `SMARTCUBE_USER`,
  `SMARTCUBE_PASSWORD`. Ver plantilla en `05_codigo/.env.example`.

> Nota: al ser una SPA con login, no se puede inspeccionar su contenido con una
> simple descarga de HTML. Para automatizar o integrar hará falta usar su API
> (endpoints que llama el frontend) o un navegador controlado (p. ej. Playwright).

#### Mapa de navegación (menú lateral)

**Principal**
- Inicio — `/`
- Consulta Catastral — `/consulta-catastral`
  - Consulta Predial — `/consulta-catastral/predial`
  - Resoluciones — `/consulta-catastral/resoluciones`
- Gestión Catastral — `/gestion-predial`
  - Asignación — `/gestion-predial/asignacion`
  - Asignación de NPN — `/gestion-predial/asignacion-npn`
  - Control de NPN — `/gestion-predial/control-npn`
  - Códigos homologados — `/gestion-predial/codigos-homologados`
- Visor — `/visor`
- Plantillas — `/plantillas`

**Herramientas**
- Área — `/area`
- Procesos Masivos — `/gestion-catastral`
  - Carga Masiva — `/gestion-catastral/carga-masiva`

**Gestión**
- Mesa de ayuda — `/mesa-ayuda`

> NPN = Número Predial Nacional (nomenclatura catastral de Colombia).

#### Flujo observado

- **Asignación** (`/gestion-predial/asignacion`): pantalla donde se revisan los
  **radicados pendientes** (trámites por asignar / en espera de gestión).
  - Columnas de la tabla: `[expandir] | Radicado | Fecha | Solicitante | Estado |
    Trámites | Validación | Acciones`.
  - **Criterio de revisión: la columna `Estado`.** Los radicados se revisan/filtran
    por su estado. El filtro de Estado es de selección múltiple (checkboxes) con buscador.
  - **Estados del flujo (ciclo de vida del radicado):** `Asignado`, `Digitado`,
    `Devuelto`, `Completado`, `Correspondencia`, `Notificado`, `Desistido`,
    `Calidad`, `Gerencia`, `Pendiente por asignar`.
  - No confundir `Estado` con la columna `Validación` (valores: `Completa` o
    `Pendiente: Técnica, Jurídica`).
  - La acción "Ver detalle" (ícono `open_in_new`) NO cambia la URL: abre un modal
    sobre la tabla.

- **Detalle del Radicado** (modal/vista de un radicado): muestra
  - **Solicitante** (nombre, documento, tipo de solicitante, dirección, correo,
    notificación email), **Resumen** (radicado, fecha, estado, nº de trámites),
    **Documentos** (adjuntos del radicado), **Trámites** (lista) y los paneles de
    **Validación Técnica** y **Validación Jurídica** (estado, quién validó, fecha, nota).
  - Cada trámite muestra: nº de trámite, tipo (p. ej. "Mutación 2a Clase - Segregación"),
    analista, estado, **NPN del predio** y el botón **"Iniciar Trámite"**.

#### Procedimiento operativo por radicado (estado Asignado)

Flujo que se repite para CADA radicado en estado "Asignado":

1. Menú lateral: **Gestión Catastral** → **Asignación** (`/gestion-predial/asignacion`).
2. Abrir el filtro de **Estado**, desplegar y marcar el checkbox **Asignado**
   (deseleccionar los demás si aplica). Confirmar.
3. Dejar **cargar la data** (la tabla se refresca con los radicados en ese estado).
4. En la columna **Radicado**, procesar en orden **de menor a mayor** (empezar por el
   radicado de número más bajo visible, p. ej. R-2026-0077).
5. En la fila del radicado, pulsar **"Ver detalle"** (ícono `open_in_new`, al final de
   la fila) para abrir el Detalle del Radicado.
6. En el Detalle, pulsar **"Iniciar Trámite"** (ícono `play_arrow`, `bg-primary`).
7. **Repetir** el ciclo (pasos 4-6) para cada radicado en estado Asignado hasta
   terminar.

> Cada ciclo = un radicado procesado. La meta global es 50 radicados (ver sección 8),
> registrando toda inconsistencia encontrada en el camino.

#### Flujo de un trámite (validaciones)

- **"Iniciar Trámite"** arranca la **parte técnica** del trámite, que es la que le
  corresponde al analista (rol del usuario: `user-analista`). Es una ACCIÓN CRÍTICA:
  cambia el estado del trámite. El REPL pide confirmación antes de ejecutarla.
- Secuencia observada del trámite: Iniciar Trámite → Validación Técnica →
  confirmación del usuario → Validación Jurídica.

**Elementos del Detalle del Radicado (ampliado, visto en R-2026-0077):**
- **Trámites:** nº de trámite, tipo, analista, estado, NPN del predio, botón
  "Iniciar Trámite", "Cargadores invitados" (botón "Invitar cargador").
- **Historial del Trámite:** eventos con usuario y marca de tiempo (Crear trámite,
  Asignar analista, Validar técnica, etc.).
- **Historial de Validaciones** (Técnica / Jurídica con estado y nota).
- **Oficio de Notificación:** indica si se requiere notificar al solicitante según
  haya rechazos.

- Al pulsar **"Iniciar Trámite"**, la plataforma navega a **`/gestion-tramites`**,
  la pantalla de trabajo de la parte técnica del analista.

#### Wizard "Gestión de Trámites" (`/gestion-tramites`)

Asistente de 8 pasos para consolidar la información predial antes de la radicación.
Encabezado: tipo de trámite (p. ej. "Mutación Integral"), radicado, predio/NPN y
"Estado Global" (p. ej. "En proceso"). Botones: "Volver al listado".

**Pasos:**
1. **PREDIO** — "Datos del Predio": descompone el NPN en campos (DEPTO, MUN, ZONA,
   SECTOR, COMUNA, BARRIO, MZ/VEREDA, TERRENO, COND, EDIF, PISO, UNID). Botón
   "Copiar NPN". Incluye **"+ Agregar foto"** (opcional) para cargar fotos.
2. PROPIETARIO
3. TERRENO
4. CONSTRUCCION
5. FUENTE ADMINISTRATIVA
6. AVALUO
7. RESUMEN
8. BORRADOR RESOLUCION

Navegación del wizard: **"Continuar"** (flecha `arrow_forward`) avanza al siguiente
paso; "Cancelar Trámite" aborta.

> NPN verificado en R-2026-0077: `763640001000000013201000000000` tiene 30 dígitos
> y los campos de pantalla reconstruyen exactamente el NPN. Estructura correcta.

---

## 6. Convenciones de trabajo

<!-- Completar: reglas que el agente debe respetar siempre -->
- Idioma de comunicación y documentación: **español**.
- **El código NO debe contener emojis** (ni en el código, ni en comentarios, ni en mensajes/logs).
- **Todos los scripts y archivos `.py` se guardan en `05_codigo/`.**
- **Los scripts temporales se BORRAN al terminar su función.** Solo permanecen
  los scripts reutilizables o que son parte estable del proyecto.
- Nomenclatura de carpetas con prefijo numérico (`01_`, `02_`, ...) y nombres en minúscula.
- Trámites nombrados como `NN_tramite_<identificador>`.

---

## 7. Herramientas descartadas

### `02_herramientas_qgis/smartcube_core.zip` — NO USAR
Es el código fuente de un plugin existente (`plugin-main`) que conecta QGIS/ArcGIS
con la API de la plataforma SmartCube para publicar/subir cartografía. Contiene:

- `qgis/smartcube_uploader/` — plugin de QGIS en PyQGIS (diálogos de carga de
  cartografía, actualización, configuración de conexión, cliente de API, CRS, iconos).
- `arcgis/` — toolbox equivalente para ArcGIS (`SmartCube.pyt`) con su `smartcube_core`.
- `docs/` — documentación de sesiones, planes y specs.
- `tests/` — pruebas de ambas implementaciones.

**Decisión:** esta herramienta queda como referencia histórica. **No se va a usar**
en este proyecto. Mantener solo a título informativo.

---

## 8. Entregable final (IMPORTANTE)

> **Meta: 50 radicados.** Al finalizar los 50 radicados se debe elaborar un
> **informe detallado y profesional** con TODAS las inconsistencias encontradas
> durante el proceso.
>
> - Ir registrando cada inconsistencia a medida que aparece: radicado, campo,
>   descripción del problema y evidencia.
> - El agente debe recordar al usuario este entregable conforme se acerque a los 50.

### Registro de inconsistencias

<!-- Tabla para ir acumulando los hallazgos durante el proceso -->

| # | Radicado | Campo / Sección | Inconsistencia encontrada | Evidencia / Nota |
|---|----------|-----------------|---------------------------|------------------|
|   |          |                 |                           |                  |

---

## 9. Herramienta de automatización (Playwright)

Para interactuar con la plataforma (navegar, hacer clic, escribir, capturar) se usa
un script de **sesión interactiva** con **Playwright** en `05_codigo/main.py`.

- Entorno gestionado con **uv** (dependencias: `playwright`, `python-dotenv`).
- Navegador: Chromium de Playwright, con **perfil persistente** en `05_codigo/.pw-profile/`
  (la sesión queda guardada tras el primer login manual; ignorado por Git).
- Capturas (HTML + PNG) en `05_codigo/capturas/` (ignorado por Git).
- Flujo: el usuario lanza `uv run main.py`, inicia sesión una vez, y queda un REPL
  (`qa>`) donde se ejecutan comandos: `goto`, `click`, `type`, `fill`, `enter`,
  `press`, `rows`, `cap`, `text`, `count`, `html`, `lote on|off`, `salir`.
- **Modo conservador:** las acciones críticas (guardar, confirmar, enviar, aprobar,
  eliminar, crear, asignar) piden confirmación antes de ejecutarse.

---

## 10. Estado de la sesión (dónde vamos)

**Última sesión: 14/10/2026.**

Avance:
- Repositorio Git inicializado y sincronizado con GitHub (último commit publicado).
- Entorno de automatización listo: `05_codigo/main.py` (Playwright + REPL `qa>`),
  perfil persistente con la sesión ya iniciada (login guardado, estable).
- Módulo en revisión: **Asignación de Radicados** (`/gestion-predial/asignacion`).
  - Página 1 mapeada (10 radicados) en `05_codigo/radicados_asignacion.csv`.
    Total: 17 radicados en 2 páginas (falta mapear la página 2).
  - Documentados los 10 estados del flujo y el flujo del trámite.
- Se abrió el **Detalle del Radicado R-2026-0089** y se capturó
  (`capturas/20261014_220443_detalle_0089.png`).
  - Trámite #95 — "Mutación 2a Clase - Segregación" — ASIGNADO.
  - NPN del predio: `763640100000001390001000000000`.
  - Validación Técnica y Jurídica: ambas "Aprobado".

Próximos pasos (retomar aquí):
1. **Validar el NPN** `763640100000001390001000000000` del Trámite #95 contra la
   estructura oficial de 30 dígitos (punto de QA pendiente).
2. Ejecutar **"Iniciar Trámite"** en R-2026-0089 para mapear en vivo los pasos del
   flujo (validación técnica → confirmación usuario → validación jurídica).
   OJO: es acción que cambia estado → el REPL pedirá confirmación (modo conservador).
3. Mapear la **página 2** de radicados (quedan 7 de 17).
4. Revisar hueco de secuencia: salto de R-2026-0081 a R-2026-0079 (¿falta 0080?).
5. Ir registrando inconsistencias en la tabla de la sección 8.

Sesión abierta: para reanudar, lanzar `uv run main.py` en `05_codigo` (la sesión
sigue guardada en el perfil).

---

## 11. Notas y pendientes

<!-- Espacio para ir anotando decisiones, dudas y tareas abiertas -->
- Definir el flujo de trabajo de un trámite catastral de principio a fin.
- Especificar el sistema de referencia de coordenadas (SRC/CRS) utilizado.
- Confirmar el detalle de los pasos de confirmación del usuario en el flujo del trámite.

---

_Última actualización: 14/10/2026_
