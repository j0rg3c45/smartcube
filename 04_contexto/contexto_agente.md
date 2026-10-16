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
   "Copiar NPN". Incluye **"+ Agregar foto"** (opcional). Las fotos las carga el
   usuario **manualmente** en el navegador (archivos en
   `03_tramites/NN_tramite_<radicado>/`).
2. PROPIETARIO
3. TERRENO
4. CONSTRUCCION
5. FUENTE ADMINISTRATIVA
6. AVALUO
7. RESUMEN
8. BORRADOR RESOLUCION

Navegación del wizard: el botón de avanzar **cambia de nombre en cada paso**:
"Continuar" (paso 1), "Siguiente Paso" (paso 2), "Continuar a Construcciones"
(paso 3), etc. "Anterior" retrocede; "Cancelar Trámite" aborta.

Detalle por paso observado:
- **Paso 2 (Propietario):** solo lectura ("solo lectura para esta mutación"). Lista
  propietarios con documento, tipo interesado, sexo, tipo derecho y % participación.
- **Paso 3 (Configuración del Terreno):** geometría (conservar/re-subir shape .zip),
  área (m²), zonas físicas y geoeconómicas (ZHG, ZHF, área gráfica/digitada, %,
  área ha, valor m², avalúo). Valida la diferencia entre área digitada y área
  geométrica contra una tolerancia (p. ej. 10% rural); marca en rojo si se supera.
  Botones: "Buscar shape del plugin", "Subir shape", "Ver en mapa", "Agregar zona".
  - Tras subir un shape nuevo, se genera **Puntos y Linderos** (vista previa del
    polígono en mapa). Hay que **describir cada lindero** (Orientación, Colinda con,
    NPN/nombre del colindante) y pulsar **"Guardar"**. El botón "Continuar a
    Construcciones" queda DESHABILITADO hasta describir y guardar los linderos.
    Botones de linderos: "Empezar aquí", "Invertir", "Regenerar", "Guardar".
  - Estos datos de linderos los diligencia el usuario (datos técnicos reales,
    desde los documentos del trámite en `03_tramites/NN_tramite_<radicado>/`).
- **Paso 4 (Construcciones):** "Unidades de Construcción" (0 si no hay). Muestra la
  cartografía "Terreno + Construcciones". Botón de avanzar: **"Siguiente: Resumen Final"**.
  - **REGLA:** en este paso el agente SIEMPRE debe preguntar al usuario si el predio
    tiene construcciones. Si tiene, se registran las unidades antes de continuar; si
    no tiene, se continua directo.

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
| 1 | (varios) | Asignación / contador | OBSERVACION (probable comportamiento normal): el "Total Radicados" varió 17->16->17. Baja mientras un radicado está "En proceso" (tras Iniciar Trámite) y vuelve a subir cuando se resuelve/pasa a calidad. El contador parece reflejar los pendientes de gestión, no un total fijo. A confirmar si es el conteo esperado. | 17 (inicio) -> 16 (0077 en proceso) -> 17 (0077 paso a calidad). |
| 2 | R-2026-0077 | Trámite / estado | ACLARADO: "Iniciar Trámite" abre el wizard pero el radicado sigue "Asignado" hasta que se completa y se pulsa "Pasar a calidad". Al pasar a calidad, el radicado SALE del listado de Asignación. Comportamiento coherente, no es inconsistencia. | Captura 20261015_174417 (0077 ya no aparece). |

| 3 | R-2026-0077 | Trámite / Paso 3 Terreno / Área | DESCARTADO como bug: el área inicial (3.050 m²) estaba fuera de la tolerancia del 10% (17,8% del polígono) y la plataforma lo marcó en rojo. Tras subir el shape correcto, el % pasó a 100% y la alerta desapareció. La validación de tolerancia FUNCIONA (comportamiento esperado, no inconsistencia). | Capturas 20261015_161838 (rojo) y 20261015_163336 (corregido). |

| 4 | R-2026-0077 | Trámite / Paso 3 / Puntos y Linderos | No se pueden COPIAR los NPN de los predios colindantes por ningún lado: el usuario tuvo que digitar manualmente cada NPN del colindante en el campo "NPN o nombre del colindante". No hay forma de copiar el NPN desde el mapa ni desde otra vista. Afecta la usabilidad y es propenso a errores de digitación. Redacción técnica en sección 8.1. | Capturas 20261015_164646 / 20261015_164851. Confirmado por el usuario. |

| 5 | R-2026-0077 y R-2026-0075 | Paso 2 Propietario / % Participación | CONFIRMADO (patrón en 2 predios). El propietario único con derecho "Dominio" llega con % de participación = 0 (valor "0E-10"), cuando lo correcto para un único propietario es 100%. En R-2026-0075 el analista tuvo que CORREGIRLO manualmente a 100 en el editor de propietario. La plataforma no autocompleta el 100% para propietario único. | R-2026-0077 (SANDRA MONICA, 0%) y R-2026-0075 (BERMUDEZ..., 0E-10 corregido a 100). Captura 20261016_180805. |
| 6 | R-2026-0077 | Paso 7 Resumen / Fuente administrativa | DESCARTADO: era un falso positivo (el HTML estaba a medio cargar). Con el resumen cargado, los datos se muestran bien. No es inconsistencia. | HTML intermedio sin terminar de cargar. |
| 7 | R-2026-0077 | Paso 7 / Validación topológica | VALIDACION CORRECTA (no es bug): el sistema detectó 2 errores que bloquean avanzar: (a) CUSTOM_TERRENO_TRASLAPE_VECINO: el terreno (predio 593) se traslapa 7.82 m² con el vecino 76364...10020 (predio 5); (b) FIJA_TRASLAPE_COLINDANTE: traslape con predio 76364...10020. El botón "Pasar borrador acto administrativo" queda bloqueado. La validación de solapes/topología FUNCIONA. | Captura 20261015_165946_paso7_errores. 2 Errores, 0 Warnings, 42 OK. |

> OBSERVACION: el shape subido en el Paso 3 corrigió el área (a 3.672,97 m², 100%) pero
> introdujo un traslape de 7.82 m² con el predio vecino. Para resolver: subir el vecino
> como colindante con geometria corregida o ajustar la geometria del tramite.
>
> RESUELTO (15/10/2026, re-validacion 5:39 p.m.): tras corregir la geometria, la
> validacion quedo en 0 Errores, 0 Warnings, 44 OK. El boton "Pasar borrador acto
> administrativo" se habilito. Confirma que la validacion topologica funciona de punta
> a punta (bloquea con error, libera al corregir).

| 8 | (general) | Captura de NPN / validación | Los campos de captura del Número Predial Nacional (NPN) NO validan longitud: permiten ingresar cadenas con longitud arbitraria (menor o mayor a los 30 dígitos oficiales), sin restricción en interfaz ni en capa de negocio. Riesgo de inconsistencias en BD, reprocesos y desalineación con el Sistema Catastral Multipropósito y las ORIP. | Redacción técnica completa para el informe en la sección 8.1. Aportado por el usuario. |

> Nota: hallazgos marcados "por confirmar" aún no son definitivos; se validan antes del informe.

### 8.1 Redacción técnica para el informe (hallazgos elaborados)

> Textos listos para el apartado de Recomendaciones / Hallazgos Técnicos del informe final.

#### Validación y control de longitud en la captura del Número Predial Nacional (NPN)

**Hallazgo / Diagnóstico actual:**

En los módulos y formularios actuales de captura de datos (como el evidenciado
durante la tramitación de expedientes con efectos registrales), los campos destinados
a la digitación del Número Predial Nacional (NPN) carecen de restricciones y
validaciones a nivel de interfaz de usuario y capa de negocio. Esto permite el ingreso
erróneo de cadenas con longitudes arbitrarias (tanto menores como mayores a los 30
caracteres requeridos), lo cual genera inconsistencias en la base de datos, reprocesos
en la expedición de actos administrativos y riesgos de desalineación con la información
del Sistema Catastral Multipropósito y las Oficinas de Registro de Instrumentos
Públicos.

**Recomendación:** implementar validación de longitud fija (30 dígitos) y de
estructura del NPN tanto en la interfaz de usuario (bloqueo/alerta al digitar) como en
la capa de negocio (rechazo en el guardado), antes de permitir avanzar el trámite.

#### Funcionalidad de copiado y reutilización del NPN en el módulo de colindantes y linderos

**Hallazgo / Diagnóstico actual:**

Durante el diligenciamiento y edición de la información de linderos y colindancias de
un predio, la interfaz no ofrece un mecanismo nativo o accesible para copiar el Número
Predial Nacional (NPN) directamente desde el módulo. Esta limitación obliga al operador
a digitar manualmente el código de 30 caracteres o a cambiar repetidamente de pantalla
o ventana para copiarlo y pegarlo, lo que ralentiza el flujo de trabajo, genera fatiga
en la digitación y eleva la probabilidad de errores tipográficos en las relaciones de
colindancia.

**Recomendación:** habilitar un botón de "copiar NPN" funcional en el listado de
predios/colindantes y permitir seleccionar el NPN de un predio vecino desde el mapa o
desde un buscador integrado, de modo que se autocomplete el campo "NPN o nombre del
colindante" sin digitación manual.

---

## 9. Herramienta de automatización (Playwright, 2 scripts)

Para interactuar con la plataforma se usa **Playwright** con una arquitectura de
**dos scripts** en `05_codigo/`, de modo que el navegador se puede dejar abierto y
el código de comandos se puede actualizar sin reiniciar el navegador:

1. **`navegador.py`** — se lanza UNA vez (`uv run navegador.py`). Abre Chromium con
   perfil persistente (`.pw-profile/`) y un puerto de depuración (CDP, por defecto
   9222). Se deja corriendo; la sesión del login queda guardada.
2. **`qa.py`** — el REPL (`uv run qa.py`). Se **conecta por CDP** al navegador ya
   abierto. Si se actualiza el código, basta cerrar `qa.py` (Ctrl+C) y relanzarlo:
   **el navegador y la página NO se reinician**.

- Entorno gestionado con **uv** (deps: `playwright`, `python-dotenv`).
- Puerto CDP configurable con `CDP_PORT` en `.env` (por defecto 9222).
- Capturas (HTML + PNG) en `05_codigo/capturas/` (ignorado por Git).
- **Comandos del REPL:** `goto`, `url`, `click`, `type`, `fill`, `press`, `enter`,
  `wait`, `text`, `count`, `html`, `rows`, `asignacion`, `estado`, `radicados`,
  `detalle`, `iniciar`, `agregarfoto`, `subirfoto`, `continuar`, `cap`,
  `lote on|off`, `salir`.
- **Modo conservador:** las acciones críticas (guardar, confirmar, enviar, aprobar,
  eliminar, crear, asignar, iniciar) piden confirmación antes de ejecutarse.
- **Operación:** cuando el usuario dice "comencemos", el agente DA los comandos a
  ejecutar; el usuario los corre y comparte la salida/captura.

> `main.py` (versión monolítica anterior) quedó reemplazado por `navegador.py` + `qa.py`.

---

#### Tipos de trámite observados

- **Efectos Registrales - Actualización Linderos Artículo 6.1** (R-2026-0077,
  "Mutación Integral"). Es el tipo de trámite que se está procesando en las pruebas.
- Mutación 2a Clase - Segregación (R-2026-0089, Trámite #95).
- **Rectificaciones - Errores Inscripción Catastral** (R-2026-0075, Trámite #78).
  NPN `763640100000016640901921040001` (30 dígitos, longitud correcta; posición 22 = 9,
  con edificio/piso/unidad, es unidad en PH / apartamento). Validaciones técnica y
  jurídica ya aprobadas por el analista. Sigue el mismo flujo de wizard.
  - En este trámite SÍ se **añade una dirección** al predio en el Paso 1 (botón
    "+ Añadir Dirección" -> modal "Nueva dirección", datos estructurados según LADM).
  - **REGLA:** en el Paso 1 (PREDIO), el agente SIEMPRE debe preguntar al usuario si
    desea o no agregar una dirección al trámite. Si sí, se diligencia el modal; si no,
    se continúa.

> Particularidades del tipo **Rectificaciones - Errores Inscripción Catastral**
> (vistas en R-2026-0075), que lo diferencian del de Efectos Registrales:
> - Paso 1: se AÑADE una dirección al predio y se diligencia la "Caracterización LADM"
>   (Tipo de Predio, Tipo de Derecho; la Condición es readonly, derivada del NPN).
> - Paso 2 (Propietario): NO es solo lectura; se puede EDITAR el propietario y agregar
>   nuevos interesados. Aquí fue donde se corrigió el % de participación de 0 a 100.

#### Formulario "Nueva dirección" (Paso 1, estructurada LADM)

Campos: Tipo de dirección (Estructurada/No Estructurada), checkbox "principal";
**Vía Principal** (Clase de vía, Valor, Letra); **Vía Generadora** (Sector ciudad,
Valor, Letra, Sector predio); Número del predio; Código postal (6 dígitos);
**Complemento** (botón "Agregar segmento", p. ej. Apartamento 301); "Nombre del predio"
(readonly, se arma solo). Botones "Cancelar"/"Agregar". Clases de vía: Avenida Calle,
Avenida Carrera, Avenida, Autopista, Circunvalar, Calle, Carrera, Diagonal,
Transversal, Circular.

> El tipo "Efectos Registrales" se trabaja con el wizard de 8 pasos de Gestión de
> Trámites (predio, propietario, terreno/linderos, construcciones, fuente
> administrativa, avalúo, resumen, borrador de resolución).

---

## 10. Estado de la sesión (dónde vamos)

**Sesión 15/10/2026 — R-2026-0077 COMPLETADO (pasó a calidad).**

- **R-2026-0077 procesado de punta a punta.** Se resolvió el traslape (re-validación
  0 errores / 44 OK), se generó el borrador de resolución y se pulsó **"Pasar a
  calidad"**. El radicado salió del listado de Asignación (pasó a estado Calidad).
- **Primer radicado completo de la meta de 50.**

#### Flujo técnico completo del analista (VALIDADO de punta a punta)

> **IMPORTANTE: este flujo es el MISMO para todos los trámites.** El primero
> completado fue de tipo "Efectos Registrales - Actualización Linderos Art. 6.1"
> (R-2026-0077), pero el resto de radicados se procesan con estos mismos pasos.
> Es el procedimiento de referencia para cada uno de los 50.

1. Asignación -> filtrar estado "Asignado" -> abrir detalle del radicado menor.
   - **Según la columna Validación:**
     - Si está "Completa" (técnica y jurídica ya aprobadas, como R-2026-0077): se puede
       iniciar el trámite directo.
     - Si está "Pendiente: Técnica, Jurídica" (como R-2026-0075): el analista debe
       hacer PRIMERO las validaciones técnica y jurídica en el detalle del radicado,
       y luego iniciar el trámite.
2. "Iniciar Trámite" -> navega al wizard `/gestion-tramites`.
3. **Wizard de 8 pasos:** Predio (foto) -> Propietario (lectura) -> Terreno
   (shape + linderos + Guardar) -> Construcciones (preguntar si tiene) -> Fuente
   Administrativa (formulario) -> Avalúo (calcular retroactivo) -> Resumen
   (validaciones: deben quedar en 0 errores) -> Borrador Resolución (editor + PDF).
4. "Pasar a calidad" -> completa la parte técnica; el radicado sale de Asignación.

Botones de avance por paso: "Continuar" / "Siguiente Paso" / "Continuar a
Construcciones" / "Siguiente: Resumen Final" / "Siguiente" / "Pasar borrador acto
administrativo" / "Pasar a calidad". (El nombre cambia por paso; a veces el primer
clic no registra y hay que repetirlo.)

Arquitectura de trabajo activa:
- `navegador.py` (Chrome CDP, perfil persistente) + `qa.py` (REPL de comandos).
- Comandos: asignacion, estado, radicados, abrir, siguiente, detalle, iniciar,
  agregarfoto, subirfoto, continuar, cap, click, type, fill, etc.

**CIERRE sesión 15/10/2026.** Trabajo guardado y repo sincronizado.

Para retomar la próxima vez:
1. Lanzar `uv run navegador.py` y `uv run qa.py` (dos terminales).
2. Procesar el siguiente radicado en Asignado: el menor es **R-2026-0079** (EMPRESA46).
   Usar el mismo flujo de 8 pasos (comando `abrir R-2026-0079` o `siguiente`).

Progreso meta: **1 de 50 radicados completos.**

Hallazgos para el informe final (ver secciones 8 y 8.1):
- #4 — NPN de colindantes no se pueden copiar (redacción técnica lista en 8.1).
- #5 — Propietario único con Dominio al 0% de participación (por confirmar).
- #8 — Falta validación de longitud del NPN (30 dígitos) (redacción técnica lista en 8.1).
- Validaciones que SÍ funcionan (no son bugs): tolerancia de área (#3), traslape
  topológico (#7). Hallazgos #1, #2, #6 aclarados/descartados.

---

### Historial anterior (14/10/2026)

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

_Última actualización: 15/10/2026_
