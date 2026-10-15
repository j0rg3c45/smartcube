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
| `05_codigo` | Código fuente | Scripts y desarrollo (p. ej. PyQGIS / Python) |

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

<!-- Completar: ¿qué se espera que haga el agente en este proyecto? -->
- Dar soporte al desarrollo y automatización del flujo catastral.
- Trabajar sobre el código en `05_codigo`.
- Procesar y organizar información de los trámites en `03_tramites`.

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

## 8. Notas y pendientes

<!-- Espacio para ir anotando decisiones, dudas y tareas abiertas -->
- Definir el flujo de trabajo de un trámite catastral de principio a fin.
- Especificar el sistema de referencia de coordenadas (SRC/CRS) utilizado.

---

_Última actualización: 14/10/2026_
