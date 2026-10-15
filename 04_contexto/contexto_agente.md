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
  <!-- Pendiente: documentar los campos del listado (nº radicado, estado, fecha,
  responsable, etc.) y las acciones disponibles sobre cada radicado. -->

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

## 10. Notas y pendientes

<!-- Espacio para ir anotando decisiones, dudas y tareas abiertas -->
- Definir el flujo de trabajo de un trámite catastral de principio a fin.
- Especificar el sistema de referencia de coordenadas (SRC/CRS) utilizado.

---

_Última actualización: 14/10/2026_
