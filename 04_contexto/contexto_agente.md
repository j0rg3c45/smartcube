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

| 9 | R-2026-0075 | Paso 4 Construcción / UC A / Calificación | La unidad de construcción (apartamento ya existente en catastro) llegó SIN calificación catastral (Estructura, Acabados, Baño, Cocina todo en "Sin selección") y SIN año de construcción. El analista debe llenar toda la calificación desde cero. A confirmar si es esperado en Rectificaciones o dato faltante de origen. | Capturas 20261016_181453 / 182104. |
| 10 | R-2026-0075 | Paso 4/7 Construcción / UC A / Año | CONFIRMADO por la validación del Paso 7 (warning CUSTOM_UC_ANIO_CONSTRUCCION): "año de construcción 5 fuera de rango (1500-2026)". El año "5" es implausible; debe ser un año real. La plataforma lo detecta correctamente como warning. | Captura 20261016_182941. |
| 11 | R-2026-0075 | Paso 7 / Validación UC altura | Error 2_CLUC_CF_81: "UC #1: planta con altura=None (debe ser > 0)". La planta de la unidad de construcción no tiene altura asociada; la plataforma exige altura > 0. Validación correcta; revela dato de altura faltante. | Captura 20261016_182941. |
| 12 | R-2026-0075 | Paso 7 / Dirección estructurada | Error 3_ET_CF_112: en la dirección estructurada original "Carrera 21AS # 21A - 11 BQ 21 AP 401 SEC J 3" el campo "Nombre" del predio viene DILIGENCIADO cuando en direcciones estructuradas debe ir VACÍO (el texto lo componen las variables de vía). Dato de origen inconsistente que bloquea el trámite. | Captura 20261016_182941. Validación correcta de la plataforma. |
| 13 | R-2026-0075 | Paso 6 / Avalúo retroactivo | La plataforma NO permite corregir/ajustar el avalúo retroactivo una vez calculado. En este caso se eligió recalcular desde 2016 y luego no dejó modificar/ajustar ese cálculo. Afecta cuando el analista necesita rehacer el retroactivo (p. ej. tras corregir datos de construcción que cambian el avalúo). Inconsistencia/limitación a confirmar. | Reportado por el usuario. Paso 6 Avalúo, R-2026-0075. |

| 14 | R-2026-0072 (Asignación de NPN) | Carga de geometría / topología | Al subir el archivo **GeoJSON** (geometría del predio), la plataforma NO arroja los errores de topología (solapes/traslapes con colindantes) que sí detecta por otras vías. Queda el tema de los colindantes sin ajustar/validar al cargar por GeoJSON. Riesgo: entra geometría con problemas topológicos sin alerta. TENER EN CUENTA PARA EL INFORME. | Reportado por el usuario en el flujo de Asignación de NPN de R-2026-0072. |

| 15 | R-2026-0072 | Paso 1 / Número de Matrícula | El campo "Número de Matrícula" debe ser SOLO numérico (no lleva el código ORIP ni guion). Poner "370-125478" fue rechazado por la validación CUSTOM_PREDIO_CF_MATRICULA_NUMERICA; lo correcto es solo el folio (125478). Validación correcta de la plataforma. | Captura 20261019_173710. |
| 16 | R-2026-0072 | Paso 7 / Destino vs Construcción | La plataforma valida que un predio con destino Habitacional/Comercial/Industrial DEBE tener al menos una unidad de construcción (CUSTOM_DESTINO_REQUIERE_UC). Si es un lote sin construcción, el destino debe ser tipo "Lote Urbanizado No Construido". Validación correcta. | Captura 20261019_173710. |
| 17 | R-2026-0072 | Paso 7 / Traslape de terreno (topología) | CUSTOM_TERRENO_TRASLAPE_VECINO: el terreno (predio 112067) se traslapa 55.40 m² con el vecino 763640100000004630801000000000 (predio 31598). El error SOLO se detecta en la plataforma (al validar en el Paso 7), DESPUÉS de cargar la geometría. El analista no tiene cómo validar/prever el traslape antes porque no cuenta con esa validación topológica en QGIS. RECOMENDACIÓN (ver 8.1). | Captura 20261019_173911. |
| 18 | R-2026-0057 | Paso 2 Propietario / % Participación + solo lectura | En trámites tipo **Efectos Registrales - Actualización Linderos Art. 6.1** (Mutación Integral) el Paso 2 Propietario es **solo lectura** ("solo lectura para esta mutación"). El propietario único (BETTY GUILLERMINA ORTIZ MAFLA, CC 000051636025, Dominio) llega con **% Participación = 0%** y **Sexo vacío (—)**, pero al ser solo lectura el analista NO PUEDE corregirlo en la plataforma. Combina el hallazgo #5 (0% en propietario único) con el agravante de que no hay forma de subsanarlo en este tipo de trámite. | Captura 20261020_085929_paso2_0057. Confirma patrón de #5 en R-2026-0077 y R-2026-0057. |
| 19 | R-2026-0057 | Paso 3 Terreno / Puntos y Linderos | USABILIDAD/RENDIMIENTO: cuando el polígono del terreno tiene MUCHOS vértices, la descripción de Puntos y Linderos se vuelve muy larga y tediosa. En este predio hay **55 puntos y 55 linderos (110 filas) por describir** manualmente (Tipo de punto, Método, Punto de control por cada punto; y cada lindero). El botón "Continuar a Construcciones" queda bloqueado hasta describir las 110 filas. No hay forma de aplicar un valor en bloque / masivo a todas las filas, lo que hace el paso costoso en tiempo para polígonos con muchos vértices. TENER EN CUENTA: este paso es MUY LARGO si el polígono tiene muchos vértices. | Captura 20261020_090854_pantalla. "110 fila(s) sin describir". |
| 20 | R-2026-0057 | Tipo Efectos Registrales / Paso 4 Construcción y demás data | En trámites tipo **Efectos Registrales - Actualización Linderos Art. 6.1 (Mutación Integral)** el trámite NO permite **actualizar/completar las construcciones** ni editar **la demás data** mientras se revisa la información del trámite. La Unidad de Construcción A llega incompleta (Año = vacío, Área gráfica = — / Total gráfica 0.00 m², sin polígono cargado) pero el analista NO puede complementarla ni corregirla (paso de solo lectura / sin edición). Esto impide subsanar datos faltantes que luego generan warnings/errores en el Paso 7 (año fuera de rango, planta con altura=None). Limitación relevante: en este tipo de trámite el analista no tiene herramientas para dejar la información completa. | Captura 20261020_093151_paso4_0057. UC Año=— , Total gráfica 0.00 m². Confirmado por el usuario. |
| 21 | R-2026-0057 | Paso 7 Resumen / CONTRADICCIÓN bloqueante (UC sin geometría) + dato de origen IGAC | CONTRADICCIÓN GRAVE DE LA PLATAFORMA: el Paso 7 arroja **1 ERROR que bloquea avanzar** -> `2_CT_CF_25` CONSISTENCIA TOPOLÓGICA: "UC #1 (A) sin geometría. Se deben verificar que todas las unidades de construcción tengan geometrías asociadas." PERO en este tipo de trámite (Efectos Registrales) el Paso 4 de Construcción NO permite cargar/editar la geometría de la UC (hallazgo #20). Resultado: el trámite exige una geometría de la UC que NO da forma de cargar desde el flujo, dejando el trámite BLOQUEADO sin posibilidad de subsanar desde la plataforma. El botón "Pasar borrador acto administrativo" queda deshabilitado. **CAUSA RAÍZ (comunicada por el equipo):** el ing. Edgar, tras hablar con el ing. Jhonny, indicó que este trámite presenta un ERROR EN LA CONSTRUCCIÓN que viene **POR DEFECTO desde el IGAC** (así fue entregada la data de origen). La UC sin geometría NO es error de captura del analista, sino de los datos de origen. DECISIÓN: el trámite queda con la data ya subida; no se fuerza el paso a calidad. Validaciones: 1 error, 1 warning, 42 OK. | Captura 20261020_094857_paso7_validado. Error 2_CT_CF_25. Nota en 03_tramites/05_tramite_R-2026-0057/NOTA_estado_tramite.txt. |
| 22 | R-2026-0057 | Paso 1 / Caracterización LADM NO editable | CONFIRMADO (usuario + automatización): la "Caracterización LADM del Predio" (Tipo de Predio, Tipo de Derecho) está requerida pero sus desplegables están **deshabilitados/readonly**; NI el usuario NI la automatización pueden complementarla (TimeoutError al intentar seleccionar, porque el control no es interactuable). El usuario confirma que es un tema de DESARROLLO de la plataforma (no depende del analista). Sumado a #20 y #21, evidencia que en Efectos Registrales el flujo exige datos (caracterización LADM, geometría de UC) que no deja completar y luego bloquea en el Paso 7. CONTRADICCIÓN DE DISEÑO: campos obligatorios no editables que impiden cerrar el trámite. | Salida REPL: "No se pudo elegir Tipo de Predio/Derecho: TimeoutError". Confirmado por el usuario. |
| 23 | R-2026-0061 | Paso 7 Resumen / Área gráfica del terreno (EXACTITUD TEMÁTICA) | El predio tiene un **ERROR EN EL ÁREA GRÁFICA DEL TERRENO que NO deja pasar** el trámite: hay diferencia entre el área entregada (digitada) y el área del polígono. Validación `3_ET_CF_108` EXACTITUD TEMÁTICA: "Área digitada 328.00 m² frente al polígono 225.73 m²: difieren 45.3%, por encima del 10% permitido. Corrija el área o la geometría." El trámite queda bloqueado en el Paso 7 por esta inconsistencia entre área entregada y área del polígono. (IMAGEN SOPORTE: la carga el usuario). | Captura 20261021_093703_pantalla. Imagen soporte pendiente de cargar por el usuario. |

> Nota: hallazgos marcados "por confirmar" aún no son definitivos; se validan antes del informe.

### REGLA de coherencia: Destino Económico vs Construcción

Si el predio NO tiene unidades de construcción (es un lote), el **Destino Económico NO
puede ser "Habitacional"** (ni otro que implique edificación). Debe usarse un destino
tipo lote, p. ej. **"Lote Urbanizado No Construido"**. La plataforma valida esta
coherencia en el Paso 7 (Resumen) y marca error si hay destino habitacional sin
construcción. (Al rellenar predios de prueba: si no se agrega construcción, elegir un
destino de lote; si se agrega construcción, puede ser Habitacional/Comercial/etc.)

> REGLA (Paso 1, Destino Económico en tramites CON construccion): si el tramite implica
> construccion (p. ej. Mutacion 3a - Cambio Area Construida), y el predio viene como
> "Lote Urbanizado No Construido", hay que CAMBIAR el Destino Economico a uno coherente
> con un predio edificado (Habitacional por defecto; en otros tramites el agente elige
> el mas logico: Comercial, Industrial, etc. segun el caso). No dejar destino de lote si
> va a tener construccion (si no, el Paso 7 marcara error de coherencia destino-UC).
>
> REGLA (coherencia Destino vs DIRECCION/tipo de predio): el destino debe ser COHERENTE
> con lo que indica la direccion. Si la direccion dice APARTAMENTO / CASA (predio
> residencial, p. ej. "...APARTAMENTO 305 TORRE C"), el Destino se mantiene/pone
> HABITACIONAL (NO cambiar a Comercial/Industrial). Confirmado en R-2026-0084 (Cambio
> Destino Economico): aunque el tramite es de cambio de destino, por ser un apartamento
> el destino se MANTIENE Habitacional. El cambio de destino aplica solo si el uso real
> del predio cambia de forma coherente.

### Mejora pendiente: automatizar pasos repetitivos del wizard

El usuario quiere que los pasos repetitivos del wizard (Fuente Administrativa con datos
de prueba, cálculo de avalúo retroactivo, navegación entre pasos) se hagan de forma
automática. Pendiente: crear en `qa.py` comandos de alto nivel (p. ej. `fuenteadmin`,
`avaluo <año>`) que rellenen de corrido con datos de prueba, dejando al usuario solo lo
que varía (dirección, propietario, shape/geometría, año del retroactivo).

### REGLA: procesamiento en LOTE + resumen.txt por tramite

Modo de trabajo en lote sobre los radicados en estado Asignado (pendientes):

- **Alcance por tramite:** avanzar y completar autonomamente TODOS los campos editables
  de los pasos 1 a 6 (datos, formularios, desplegables, metadatos). En los pasos
  cartograficos (Terreno paso 3, Construccion paso 4) diligenciar solo lo alfanumerico
  permitido y dejar preparado el punto para que el USUARIO cargue/ajuste la geometria.
  El Paso 7 es Resumen/consolidacion.
- **Datos al azar NO repetidos:** nombres, apellidos, documentos ficticios, direcciones,
  numeros de documento fuente y observaciones aleatorios. Alternar nombres masculinos y
  femeninos. PROHIBIDO duplicar titulares, nombres completos o numeros de identificacion
  entre tramites. Mantener registro de lo usado (lista "Datos de prueba usados").
- **Coherencia y validez:** aunque ficticios, los datos deben tener logica catastral
  (fechas en rango valido, NPN 30 digitos, matricula solo numerica, tipo de documento
  acorde a persona natural/juridica).
- **ENTREGABLE por tramite:** generar `resumen.txt` (o `resumen_<RADICADO>.txt`) dentro
  de la carpeta local del tramite (`03_tramites/NN_tramite_<RADICADO>/`) con:
  1. Identificacion: radicado, ID del tramite (Tramite #), tipo de tramite exacto.
  2. Datos ingresados: titulares/propietarios generados, documentos ficticios, y datos
     principales cargados de los pasos 1 a 6.
  3. Puntos pendientes de intervencion: que informacion cartografica (terreno o
     construcciones) queda pendiente para que el usuario la cargue/ajuste.
  4. Estado en plataforma: estado exacto en que queda el tramite.

> NOTA operativa: el componente cartografico (Terreno/Construcciones) es RESERVA del
> usuario. Como el Terreno (paso 3) va antes de Fuente Administrativa (5) y Avaluo (6),
> el alcance alfanumerico autonomo por tramite llega hasta el punto donde la plataforma
> exige geometria; los pasos posteriores a la geometria se completan despues de que el
> usuario cargue el poligono. Algunos tipos (Mutacion 2a/5a, Cambio de NPN) exigen
> Asignacion de NPN (geometria) ANTES del wizard.

### REGLA: separacion de roles alfanumerico (agente) vs cartografico (usuario)

Division de tareas acordada para procesar tramites:

- **Agente (autonomo, pasos alfanumericos 1 a 6):** conduce el avance por las etapas del
  tramite, diligencia TODOS los formularios, campos de texto, fechas, selectores,
  checklists y metadatos con datos sinteticos no repetidos, y gestiona confirmaciones,
  guardados de fase y transiciones de estado. El agente da los comandos exactos a correr
  (el usuario solo los ejecuta en la terminal y pega la salida; no decide ni digita
  campos alfanumericos).
- **Usuario (unica intervencion, componente GIS/cartografico):** terreno (poligonos de
  predio) y construcciones los gestiona el usuario manualmente en el visor SIG.
- **Punto de pausa cartografico:** cuando el flujo llegue a modificar/confirmar
  geometrias de terreno o construcciones, el agente DETIENE la ejecucion y notifica
  textualmente: "Paso cartografico alcanzado en el tramite [ID/Tipo]. Queda en espera de
  tu intervencion manual sobre terreno/construcciones." Espera la palabra clave del
  usuario (`listo` o `continuar`) para retomar y automatizar los pasos restantes.
- **Errores en pasos alfanumericos:** ante bloqueo o error de UI, el agente toma
  captura, genera log del campo/paso donde ocurrio y lo reporta al usuario.

> NOTA de arquitectura: el agente NO controla el navegador directamente. La
> automatizacion corre con Playwright (`navegador.py` + `qa.py`); el usuario ejecuta los
> comandos que el agente le pasa. "Autonomo" = el agente conduce cada paso y provee el
> comando/datos; el usuario es el ejecutor. Lo unico que el usuario decide es la parte
> cartografica.

### Validador automatico en lote (validador_qa.py)

Script autonomo `05_codigo/validador_qa.py` que valida tecnica+juridica de varios
radicados de corrido (se conecta por CDP al navegador abierto, busca cada radicado por
el buscador, abre detalle, valida NPN y aprueba ambas validaciones). Genera reporte CSV
+ log en `05_codigo/reportes/` y capturas en `capturas/`.
- Uso: `uv run validador_qa.py R-2026-XXXX R-2026-YYYY ...` (o `--dry-run` para probar).
- **`--todos`**: detecta y valida TODOS los Pendientes recorriendo TODAS las paginas
  del listado (asi toma radicados nuevos sin lista manual).
- **`--vigilar --intervalo N`**: modo continuo, revisa cada N segundos y valida los
  nuevos pendientes que vayan apareciendo (no repite los ya hechos).
- Dry-run del 19/10/2026 OK: proceso los 9 radicados pendientes, leyo NPN (todos 30
  digitos) y estados correctamente.

### Procesamiento en LOTE del flujo alfanumerico (lote_qa.py)

Script `05_codigo/lote_qa.py` que procesa en lote el flujo alfanumerico de los tramites
en Asignado. Se conecta por CDP al navegador abierto (reutiliza funciones de `qa.py`),
y por cada radicado: busca, abre detalle, lee tipo/ID/NPN, valida tecnica+juridica si
esta Pendiente, inicia el wizard y AVANZA lo mas lejos posible llenando lo alfanumerico
editable de cada paso.

- **Avance maximo:** si la plataforma deja continuar sin geometria, el script avanza
  hasta el Paso 7 (Resumen). Si un paso cartografico (Terreno paso 3 / Construccion
  paso 4) EXIGE geometria para continuar, se detiene limpio ahi y lo marca como
  pendiente de intervencion del usuario.
- **Pasos que llena:** Paso 1 (caracterizacion LADM si editable), Paso 2 (propietario:
  registra persona sintetica unica), Paso 5 (Fuente Administrativa completa), Paso 6
  (Avaluo retroactivo del anio configurado, por defecto **2025**, SOLO en los que
  lleguen a ese paso).
- **Datos sinteticos NO repetidos:** generador con sets de unicidad (nombres completos
  y documentos) precargados con el historico; alterna masculino/femenino. Fechas y
  numeros de documento fuente aleatorios por tramite.
- **Entregable por tramite:** `resumen_<RADICADO>.txt` en la carpeta local del tramite
  (`03_tramites/NN_tramite_<RADICADO>/`) con identificacion, datos ingresados, pendiente
  cartografico y estado final. Ademas un log del lote en `05_codigo/reportes/`.
- **Excluidos por defecto:** R-2026-0057 (bloqueado por bug IGAC).
- **Conservador:** si un tramite falla o tiene algo inesperado (modal, selector), lo
  anota y sigue con el siguiente; no fuerza acciones de guardado/aprobacion criticas
  mas alla de validar/iniciar.

Uso:
    uv run python navegador.py            (terminal 1; sesion iniciada; NO DevTools)
    # PRUEBA con 1 radicado ANTES del lote completo (REGLA):
    uv run python lote_qa.py --radicados R-2026-0061
    # Lote completo (tras validar la prueba):
    uv run python lote_qa.py
    # Opcionales: --anio 2024 | --excluir R-2026-XXXX | --semilla <texto>

> REGLA: SIEMPRE hacer una PRUEBA con 1 solo radicado antes de lanzar el lote completo,
> para validar que el flujo y los selectores funcionan y no dejar varios tramites a
> medias. Cerrar el REPL `qa.py` mientras corre el lote (ambos usan el mismo navegador);
> el navegador debe seguir abierto.

#### PASO A PASO para validar (correr el validador)

Cuando haya que validar radicados (tecnica + juridica), el agente DA este paso a paso:

1. Verificar que el navegador este activo (CDP puerto 9222). Si no, lanzarlo:
   - Terminal 1: `cd C:\Users\Jorge\Desktop\Smartcube\05_codigo` y `uv run navegador.py`
     (dejar abierta; iniciar sesion una vez; NO abrir DevTools / F12).
2. En Terminal 2: `cd C:\Users\Jorge\Desktop\Smartcube\05_codigo`.
3. (Recomendado) Prueba segura, no aprueba nada:
   `uv run validador_qa.py --todos --dry-run`
   -> revisar el log en `05_codigo/reportes/` (debe listar los pendientes de TODAS
      las paginas).
4. Ejecucion real (aprueba tecnica + juridica de todos los pendientes):
   `uv run validador_qa.py --todos`
5. Para dejarlo vigilando y que valide los nuevos que aparezcan:
   `uv run validador_qa.py --vigilar --intervalo 120`  (Ctrl+C para detener).
6. Tambien se puede validar una lista puntual:
   `uv run validador_qa.py R-2026-0062 R-2026-0067 ...`

Resultados: reporte CSV + log en `05_codigo/reportes/`, capturas en `capturas/`.
Durante la corrida: NO usar el navegador ni abrir DevTools.

### Notas por tipo de trámite (revision manual 21/10/2026)

- **R-2026-0061 — Mutación 3a Clase - Cambio Área Construida:**
  - Paso 1 Predio: se EDITO la direccion a ESTRUCTURADA (Carrera 49 C # 41 B - 28,
    reutilizando el 28 de la direccion de origen) y se CAMBIO el Destino Economico de
    "Lote Urbanizado No Construido" a **Habitacional** (porque el tramite lleva
    construccion). Caracterizacion LADM readonly (Tipo Predio/Derecho en "—").
  - Paso 2 Propietario: NO requiere ajustes, viene completo (no falta nada).
  - Pasos cartograficos (Terreno/Construccion): reserva del usuario; este tramite SI
    lleva construccion. El usuario cargo la geometria (2 plantas, 212.41 m2) y se lleno
    la UC con `construccion` (calificacion conservadora). UC nueva creada OK.
  - Paso 5 Fuente Admin y Paso 6 Avaluo 2025: completados por el usuario avanzando.
  - **Paso 7 Resumen (21/10): 2 ERRORES que bloquean, 1 warning, 58 OK.** Pendiente de
    AJUSTE DEL USUARIO:
    1. `3_ET_CF_108` EXACTITUD TEMATICA: area digitada 328.00 m2 vs poligono 225.73 m2
       difieren 45.3% (> 10%). Hay que corregir el area o la geometria (cartografico).
    2. `CUSTOM_AVALUO_COMPLETO` CONSISTENCIA DE AVALUO: "UC A sin valor en tabla (zona 00,
       agro False, uso 2, puntaje 28)". El uso elegido (Apartamentos 4+ = uso 2) en zona
       00 (rural) no tiene valor en la tabla de avaluo. A revisar: cambiar el uso de la
       UC por uno con valor en tabla para esa zona; si ningun uso tiene valor -> HALLAZGO.
  - Tras ajustar, pulsar RE-VALIDAR.
  - **ESTADO FINAL (21/10/2026): R-2026-0061 QUEDO LISTO.** El usuario resolvio los 2
    errores del Paso 7 (area grafica del terreno y UC sin valor en tabla). El error de
    area grafica quedo documentado como hallazgo #23 en el informe (con imagen soporte).
    Trabajo alfanumerico del tramite completado.

> OBSERVACION para el informe (posible hallazgo): la calificacion/uso de la UC puede
> quedar "sin valor en tabla de avaluo" segun la zona (ej. uso residencial urbano en
> zona 00 rural). Validar si es limitacion de la tabla de avaluo o eleccion de uso.

### Tipo de trámite: Mutación 3a Clase - Cambio Destino Económico (R-2026-0084)

Flujo de 8 pasos. En Cambio de Destino el proceso es de CORRIDO (NO hay pausa
cartografica):
- Paso 1 Predio: direccion se deja si ya es estructurada (apartamento en PH); el Destino
  se mantiene coherente con la direccion (apartamento -> Habitacional, NO cambiar).
- Paso 3 Terreno: NO sufre cambios graficos; solo avanzar.
- Paso 4 Construccion: la geometria de la UC YA coincide (no cargar capas). La
  calificacion llega INCOMPLETA: hay que ENTRAR a EDITAR la UC y complementar todos los
  campos alfanumericos de calificacion (estructura/acabados/conservacion) con valores
  coherentes NO repetidos, y pulsar 'Actualizar'/'Guardar'.
- Pasos 5-7: Fuente Admin + Avaluo + Resumen.
- Comando: `tramite3a [semilla] [destino]` (de corrido; edita calificacion UC; NO pasa
  a calidad). El resumen.txt debe indicar: terreno intacto + calificacion de UC
  actualizada.
- **R-2026-0084 QUEDO LISTO (21/10/2026):** Mutacion 3a Cambio Destino. Direccion
  estructurada, destino Habitacional mantenido, terreno sin cambios; el usuario cargo la
  geometria de la construccion (altura), el agente edito la calificacion de la UC (año
  2010, baños/habitaciones, calificacion conservadora) + avaluo 2025. Resumen: 0 ERRORES,
  60 OK. Resumen en 03_tramites/12_tramite_R-2026-0084/resumen_R-2026-0084.txt.
- **R-2026-0088 (21/10/2026):** Mutacion 3a Cambio Area Construida, predio #23428,
  propietario JAMUNDI URBANIZADORA. El comando `tramite3a` proceso TODO lo alfanumerico
  de corrido (predio, propietario, terreno/construccion avanzados, fuente admin, avaluo)
  y llego al Resumen con 1 ERROR, 60 OK. El error es `3_ET_CF_108` EXACTITUD TEMATICA:
  area digitada 1921 m2 vs poligono 2167.96 m2 (11.4%, >10%). ES AJUSTE CARTOGRAFICO DEL
  USUARIO (corregir area/geometria del terreno) + re-validar. Pendiente ajuste del usuario.
- **REGLA (editar UC):** la informacion de la Unidad de Construccion SOLO se edita con
  el boton del icono `<span class="material-symbols-outlined text-lg">edit</span>` en la
  fila de la UC. Ese boton abre el modal "Editar UC A".
- **Campos obligatorios de la UC al editar (si no, el Paso 7 da error):**
  - **USO (OBLIGATORIO):** tras elegir Tipo unidad=Residencial, el desplegable 'Uso'
    carga sus opciones con RETARDO. Hay que ESPERAR a que aparezcan (reintentar) y elegir
    una opcion real (p. ej. "Vivienda hasta 3 pisos" o "Apartamentos 4 y mas pisos"),
    NO dejarlo en el placeholder "Usos de Residencial...". Si queda sin uso, el modal
    muestra "Falta: uso" y NO deja 'Agregar UC'/'Actualizar UC'. (El comando
    `construccion` ya reintenta hasta cargar el uso y lo fija con evento change.)
  - Año de construccion (input min=1800, max=2026; puede venir en 0).
  - Calificacion catastral completa (16 desplegables: estructura/acabados/baño/cocina).
  - Total baños / habitaciones (valores coherentes de vivienda, no 0).
  - Guardar con 'Actualizar UC'.
- **REGLA IMPORTANTE (CORRECCION): en TODAS las Mutaciones 3a hay que SUBIR la GEOMETRIA
  de la CONSTRUCCION** (el shapefile/.zip con las plantas, en el area "Cargar geometrias
  de unidades de construccion"). La ALTURA de las plantas viene de ese shape; NO se
  digita en el modal. Si NO se carga la geometria, el Paso 7 arroja `2_CLUC_CF_81`:
  "UC #N: planta con altura=None (debe ser > 0)".
  - Por tanto, la carga de la geometria de construccion es INTERVENCION DEL USUARIO
    (cartografico) y el comando `tramite3a` debe DETENERSE en el Paso 4 esperando esa
    carga. Luego el usuario retoma para completar la calificacion/avaluo/resumen.
  - Flujo correcto 3a: Paso 1 (predio) -> Paso 2 (propietario) -> Paso 3 Terreno (sin
    cambios, avanzar) -> Paso 4 Construccion: USUARIO carga el shape de la UC (plantas
    con altura) -> agente edita la calificacion de la UC (boton edit) + Actualizar ->
    Paso 5/6/7.

### Tipo de trámite: Cancelaciones - Fuerza Mayor (R-2026-0086)

Tipo "Mutación Integral / Cancelaciones - Fuerza Mayor" (R-2026-0086, Tramite #92,
NPN 763640001000000070294500000015, Predio #4216). Estructura DISTINTA y mas corta:
solo **3 pasos**: (1) Fuente Administrativa, (2) Resumen, (3) Borrador Resolucion.
NO tiene Predio/Propietario/Terreno/Construccion/Avaluo. Por eso el lote (`lote_qa.py`)
no lo pudo procesar (esperaba 7-8 pasos) y lo marco "no determinado".

- **Paso 1 Fuente Administrativa:** campo OBLIGATORIO "Motivo de la cancelacion"
  (textarea; queda en el historico y la resolucion), + los 7 desplegables de Fuente
  Administrativa estandar (iguales a `fuenteadmin`).
- Comando `cancelacion [semilla]`: llena el motivo de fuerza mayor (variado: remocion en
  masa/sismo, inundacion/ribera, socavacion/erosion, avenida torrencial; con nº de acta
  y fecha ficticia, sin repetir) + fuente administrativa, avanza al Resumen y valida.
  NO pasa a calidad (lo confirma el usuario).
  - PROBADO OK (21/10) en R-2026-0086: motivo "Predio sumergido de forma permanente por
    desbordamiento y cambio de cauce del rio el 16/06/2026, con perdida total por
    afectacion de ribera, segun informe pericial de visita de campo No. 816". Resumen:
    0 ERRORES, 0 warnings, 30 OK. Propietario DAGUA IGNACIO ZAMANATE (se conserva). Listo
    para pasar a calidad. (El conteo en consola salio '?' por el lector regex, pero la
    captura confirma 0 errores.)

### Tipos de trámite (ampliado, dry-run 19/10/2026)

- R-2026-0062: Mutación 4a Clase - Revisión Avalúo. NPN 763640100000000030012000000000.
- R-2026-0067: Mutación 2a Clase - División Material. NPN 763640100000011890106000000000.
- R-2026-0079: **Mixta**: Rectificaciones - Errores Inscripción Catastral → Mutación 1a
  Clase - Cambio Propietario (trámite combinado). NPN 763640002000000030813800004806.
- R-2026-0081: Mutación 1a Clase - Cambio Propietario. NPN 763640002000000020804800001140.
- R-2026-0082: Mutación 1a Clase - Cambio Propietario. NPN 763640100000017960801800000059.
- R-2026-0084: Mutación 3a Clase - Cambio Destino Económico. NPN 763640100000007701905903030005.
- R-2026-0085: Rectificaciones - Errores Inscripción Catastral. NPN 763640100000007730223000000000.
- R-2026-0086: (tipo no leido en dry-run). NPN 763640001000000070294500000015.
- R-2026-0087: Rectificaciones - Cambio Número Predial Nacional. NPN 763640100000011890016000000000.
- R-2026-0061: Mutación 3a Clase - Cambio Área Construida (validado manual). NPN de 32 dígitos (revisar).

### Listado de radicados Asignado (19/10/2026)

13 radicados en Asignado (2 páginas). Ordenados de menor a mayor:
`0057, 0061, 0062, 0067, 0079, 0081, 0082, 0084, 0085, 0086, 0087, 0088, 0089`.
- **R-2026-0057** (EMPRESA1, NIT 899764890): Validación **Completa** → inicia directo.
- Los demás en su mayoría "Pendiente: Técnica, Jurídica" → hacer validaciones antes.
- NOTA: el comando `listar` no lee bien la página 2 (el botón "Siguiente" de
  paginación no responde al selector; hay varios "Siguiente" en la app). Pendiente
  arreglar el selector de paginación.

### Datos de prueba usados (para NO repetir; variar en cada radicado)

Cuando se rellenan predios de prueba (entorno QA), usar datos ficticios lógicos de
Colombia y NO repetir entre radicados. Registro de los ya usados:
- R-2026-0072: Propietario **Carlos Andres Ramirez Gomez**, CC **1130598742**,
  Masculino, Dominio, 100%. Matrícula 370-125478. Dirección "Calle 10 J Norte # 5-20".
  Destino Habitacional, Tipo Predio Privado.

#### REGLA: datos sinteticos (mock data) autorizados

Autorizado el uso de **datos ficticios o generados al azar (mock data)** a criterio del
agente para TODOS los tramites, plantillas y formularios de SmartCube (entorno QA).
Directrices obligatorias:

1. **Libertad de seleccion:** el agente puede inventar o generar aleatoriamente nombres
   de personas, documentos de identidad ficticios, matriculas inmobiliarias,
   direcciones, numeros de radicado, observaciones, etc. Si se usan librerias de
   generacion (p. ej. `Faker` con locale `es_CO`), configurarlas para producir valores
   realistas acordes al tipo de campo.
2. **No repeticion (unicidad por tramite):** NUNCA repetir datos entre un tramite y
   otro. Cada registro, predio o solicitud lleva un conjunto de valores unico. Mantener
   un registro/set interno durante la ejecucion para garantizar que ningun dato clave
   generado colisione con los de tramites anteriores (IDs, nombres consecutivos,
   radicados, matriculas, etc.). Ir anotando lo usado en la lista de arriba.
3. **Cumplimiento de formato y estructura:** aunque los valores sean ficticios, deben
   respetar los formatos exigidos por la plataforma:
   - **NPN**: 30 digitos numericos exactos.
   - **Matricula inmobiliaria**: solo numerica (folio, sin codigo ORIP ni guion).
   - **Documentos de identidad**: numericos, longitud plausible para Colombia.
   - **Fechas**: formato valido; anios de construccion dentro de rango (1500-2026).
   - **Decimales/miles, textos**: longitudes y tipos validos, sin espacios ni
     caracteres residuales.
4. **Coherencia de negocio:** respetar las reglas ya documentadas (p. ej. destino de
   lote sin construccion no puede ser Habitacional; propietario unico al 100%).

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

#### Validación topológica temprana de traslapes (antes de cargar la geometría)

**Hallazgo / Diagnóstico actual:**

La detección de traslapes (solapes) entre el terreno del trámite y los predios vecinos
se realiza únicamente en la plataforma, en la etapa de validación del resumen final,
es decir, DESPUÉS de haber cargado la geometría (shape/GeoJSON). El analista no dispone
de un mecanismo de validación topológica previa en su entorno de trabajo (QGIS), por lo
que no puede identificar ni corregir los solapamientos antes de subir la geometría.
Esto genera reprocesos: cargar, validar, volver a QGIS a corregir el polígono y
recargar, de forma iterativa hasta que el traslape desaparece.

**Recomendación:** proveer una validación topológica temprana del lado del analista
(por ejemplo, un complemento o verificación en QGIS, o una herramienta de pre-validación
de geometría en la plataforma que corra antes de consolidar el trámite) que detecte los
traslapes contra los predios vecinos del catastro antes de la carga final, reduciendo
reprocesos y errores en la etapa de resumen.

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

> **REGLA Paso 6 (Avalúo):** el agente SIEMPRE debe preguntar al usuario desde qué año
> (o hasta qué año) se recalcula el avalúo retroactivo, antes de pulsar "Calcular
> retroactivo". El año de inicio se elige en el desplegable "Vigencia" y calcula desde
> ese año hasta la vigencia anterior a la actual. (En R-2026-0075 el usuario eligió 2016.)

#### Tipos de trámite observados

- **Efectos Registrales - Actualización Linderos Artículo 6.1** (R-2026-0077 y
  R-2026-0057, "Mutación Integral"). Es el tipo de trámite que se está procesando en
  las pruebas.
  - **NOTA IMPORTANTE (comportamiento de este tipo):** en Efectos Registrales la
    mayoría de pasos son de SOLO LECTURA. El trámite NO deja **actualizar/completar
    las construcciones** (Paso 4) ni **editar la demás data** (propietario, UC, etc.)
    mientras se revisa la información del trámite. Es decir, el analista solo puede
    revisar y avanzar, no complementar datos que vengan incompletos (p. ej. UC sin
    año, sin polígono/área gráfica, propietario con 0% de participación). Ver hallazgo
    en la tabla de la sección 8.
- Mutación 2a Clase - Segregación (R-2026-0089, Trámite #95).
- **Mutación 5a Clase - Predios Nuevos Formales** (R-2026-0072, Trámite #75).
  NPN `763640100000004630801000000000` (30 dígitos). Solicitante EMPRESA3. Las
  validaciones técnica y jurídica llegaron PENDIENTES; el analista las realizó
  (ambas Aprobado, observación "Todo esta Ok" / "Todo esta Ok en Juridica").
  - **PARTICULARIDAD:** este tipo de trámite REQUIERE **Asignación de NPN ANTES del
    wizard.** Al "Iniciar Trámite" muestra "Falta la Asignación de NPN" con botón
    "Ir a Asignación de NPN". Hay que: cargar el shape con los predios desde el plugin
    QGIS, asignar los NPN y **materializar** los predios en la página Asignación de NPN
    (`/gestion-predial/asignacion-npn`). Solo después se puede abrir el wizard de 8 pasos.
  - La pantalla **Asignación de NPN** tiene una lista "Trámites por numerar"; se
    selecciona el trámite, se numeran sus predios (desde la geometría del topógrafo),
    y luego se vuelve a Asignación para "Iniciar Trámite" de nuevo (ya entra al wizard).
  - **Tipos de trámite que requieren Asignación de NPN** (vistos en "Trámites por
    numerar"): Mutación 5a Clase - Predios Nuevos Formales / Informales, Mutación 2a
    Clase - División Material / Segregación / Agregación, Rectificaciones - Cambio
    Número Predial Nacional. (En "Cambio de NPN" no hay geometría: se asigna el número
    nuevo al predio que ya existe.)
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

#### Direcciones del Predio (Paso 1): editar vs añadir

En la seccion "Direcciones del Predio" del Paso 1 hay 2 opciones por cada dato:
- **Editar** la direccion existente: icono lapiz en la fila (ACCIONES).
  `<span class="material-symbols-outlined text-lg">edit</span>` (tambien hay icono de
  eliminar/papelera). Abre el modal para corregir la direccion actual.
- **Añadir** otra direccion: boton "+ Añadir Dirección" arriba a la derecha.
  `<button ...><span class="material-symbols-outlined text-base">add</span>Añadir Dirección</button>`.
  Abre el modal "Nueva direccion" (estructurada o no estructurada).

Selectores utiles:
- Editar (primera fila): `page.locator("span.material-symbols-outlined", has_text="edit").first`
  o el boton/lapiz de la fila. En REPL: `click texto=edit` (toma el primero).
- Añadir: `click button:has-text("Añadir Dirección")`.

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

**Sesión 20/10/2026 (tarde) — LOTE alfanumerico procesado con lote_qa.py.**

Se ejecuto `lote_qa.py` sobre los radicados en Asignado (excluyendo 0057 y 0061 ya
hechos). Resultado del lote (cada uno con su `resumen_<RADICADO>.txt` en su carpeta):

- **Avanzaron al Paso 7 (Resumen) completos** (Fuente Admin 7/7, avaluo 2025): R-2026-0061,
  0062 (Mut 4a Rev. Avaluo), 0079 (Mixta), 0084 (Mut 3a Cambio Destino), 0085
  (Rectificaciones), 0088 (Mut 3a Cambio Area). Faltan geometrias de Terreno y
  Construccion (reserva del usuario).
- **Requieren Asignacion de NPN** (cartografico, antes del wizard): 0067 (Mut 2a Division),
  0087 (Rectif. Cambio NPN), 0089 (Mut 2a Segregacion). El lote se detuvo limpio.
- **Detenidos en Paso 6** (avaluo 2025 calculado pero el detector no avanzo al 7):
  0081 y 0082 (ambos Mutacion 1a - Cambio Propietario). A revisar si estos tipos NO
  tienen paso de avaluo (el "Cambio de Propietario" podria no recalcular avaluo).
- **Sin determinar** (no inicio wizard, revisar manual): 0086 (#92, tipo no leido).

Confirmado que funciona: el fix de Fuente Administrativa (espera de carga de opciones +
fallback a primera opcion valida + verificacion 7/7 en el lote). Datos sinteticos unicos
por tramite (nombres/documentos no repetidos). El usuario revisa manualmente 0081, 0082,
0086 e informa.

Pendientes de afinamiento del detector (opcional): (a) tras el avaluo en Cambio de
Propietario el detector reintenta el Paso 6 y no avanza; (b) deteccion de estados raros
tipo 0086. No son criticos: el lote dejo todo lo alfanumerico lleno.

**Sesión 20/10/2026 — R-2026-0057 BLOQUEADO por bug de plataforma (Efectos Registrales).**

- Se procesó **R-2026-0057** (Efectos_Registrales - Actualización Linderos Art. 6.1,
  "Mutación Integral", Trámite #60). NPN `763640002000000030239000000000`, predio rural
  de ~13,9 ha (139.363 m2), destino Agropecuario. Validación llegó Completa -> inicio
  directo.
- Avance del wizard: Paso 1 (predio, solo lectura + foto) -> Paso 2 (propietario, SOLO
  LECTURA, 0% part.) -> Paso 3 (Terreno: 55 puntos y 55 linderos rellenados con los
  comandos masivos, orientaciones REALES desde el GeoJSON, Guardado OK) -> Paso 4
  (Construcción: UC "A" ya existente pero SIN geometría y sin año, NO editable) ->
  Paso 5 (Fuente Administrativa rellenada con `fuenteadmin`) -> Paso 6 (Avalúo
  retroactivo 2025 con `avaluo 2025`, OK) -> Paso 7 (Resumen).
- **BLOQUEO:** el Paso 7 arroja 1 ERROR (`2_CT_CF_25`: "UC #1 (A) sin geometría") que
  impide avanzar. En este tipo de trámite NO se puede cargar la geometría de la UC ni
  editar la Caracterización LADM del Paso 1 (ambos readonly). El usuario CONFIRMA que
  es un tema de DESARROLLO de la plataforma, no del analista. El trámite NO se puede
  pasar a calidad. Hallazgos #20, #21, #22.
- **R-2026-0057 queda como PROCESADO pero BLOQUEADO** (no cuenta como completado a
  calidad). **CAUSA RAÍZ confirmada (20/10/2026):** el ing. Edgar, tras consultar con
  el ing. Jhonny, indicó que el error de la UC sin geometría viene POR DEFECTO desde
  el IGAC (dato de origen), no es error de captura del analista. DECISIÓN: el trámite
  queda con la data ya subida (predio, propietario, terreno con 55 puntos/linderos,
  fuente administrativa, avalúo 2025); NO se fuerza el paso a calidad. Documentado en
  `03_tramites/05_tramite_R-2026-0057/NOTA_estado_tramite.txt` y hallazgo #21.

#### Comandos de automatización NUEVOS en qa.py (sesión 20/10/2026)

Se agregaron comandos de alto nivel para automatizar los pasos alfanuméricos del
wizard (rellenan de corrido con datos sinteticos coherentes y no repetidos):
- `entrar <R-...>` — AUTO COMPLETO: navega a Asignacion, filtra, busca el radicado por
  el buscador, abre el detalle y pulsa 'Iniciar Tramite', dejando la pagina dentro del
  wizard (/gestion-tramites). Util para ENTRAR DIRECTO a revisar cada radicado sin
  encadenar comandos. Ej: `entrar R-2026-0061`.
- `paso` — diagnostica el paso actual del wizard y dice si es automatizable (agente)
  o manual (usuario/cartografico), con la frase de pausa cuando corresponde.
- `puntosmasivo <TipoPunto>|<Metodo>|<PuntoControl>` — Paso 3 pestaña Puntos: llena
  las N filas (N = vertices) en bloque. Valores rural por defecto: Mojón / Método
  Directo / Apoyo.
- `linderosmasivo <ruta.geojson>` — Paso 3 pestaña Linderos: la ORIENTACION de cada
  lindero se calcula REAL desde el poligono (azimut de cada segmento); 'Colinda con'
  y NPN/nombre colindante son sinteticos coherentes. Tras llenar hay que pulsar
  Guardar (`click button:has-text("Guardar")`).
- `fuenteadmin [semilla]` — Paso 5: rellena toda la Fuente Administrativa (tipo fuente
  Escritura Pública, Disponible, A-Tradicion, Notaria, Valle del Cauca, Jamundí,
  naturaleza jurídica; numeros y fechas aleatorios; observacion "sin observacion").
- `avaluo <anio>` — Paso 6: elige la vigencia del retroactivo y pulsa "Calcular
  retroactivo". Ej: `avaluo 2025`.
- `caracterizacion [TipoPredio]|[TipoDerecho]` — Paso 1: llena Caracterización LADM
  (Privado / Dominio). OJO: en Efectos Registrales esos controles son READONLY y el
  comando dara TimeoutError (no es error del comando, es que la plataforma no deja).
- `editardireccion [semilla]` — Paso 1: edita la direccion del predio dejandola
  ESTRUCTURADA (LADM). Abre el modal de editar (si no esta), cambia 'Tipo de direccion'
  a Estructurada, llena Via Principal (clase de via + valor + letra), Via Generadora
  (valor + letra), Numero del predio y Codigo postal con datos sinteticos unicos, y
  pulsa Actualizar. Probado en R-2026-0061 (quedo "Carrera 49 C # 41 B - 71").
  REGLA: cuando el usuario diga "editar la direccion", SIEMPRE dejarla ESTRUCTURADA.
  REGLA (IMPORTANTE): si la direccion YA es **Estructurada** y esta bien, NO se toca
  (no editar ni re-generar). Solo se edita/estructura cuando la direccion es "No
  Estructurada". Confirmado en R-2026-0084 (apartamento en PH, direccion estructurada OK).
  REGLA de direcciones:
   (a) NO repetir direcciones entre tramites (unicidad, como los demas datos sinteticos).
   (b) Si la direccion ANTERIOR trae numeros (p. ej. "Mz C Lo 28 Km 1..." tiene 28 y 1),
       REUTILIZAR alguno de esos numeros en la direccion estructurada editada, para
       mantener coherencia con el dato de origen (la direccion trae pistas).
- `destino [valor]` — Paso 1: cambia el Destino Económico (def. Habitacional). Usar en
  tramites CON construccion para no dejar destino de lote (si no, el Paso 7 marca error
  de coherencia destino-UC). Ej: `destino Habitacional` / `destino Comercial`.
- `construccion [anio] [semilla]` — Paso 4: llena el modal 'Nueva unidad de construccion'
  con datos sinteticos de vivienda: tipo Residencial, uso, año (param o aleatorio
  1990-2020), estado, y la CALIFICACION CATASTRAL completa (16 desplegables:
  estructura/acabados/baño/cocina) + observaciones. Requiere que la GEOMETRIA (plantas)
  ya este cargada por el usuario. Luego revisar y pulsar 'Agregar UC'
  (`click button:has-text("Agregar UC")`). Probado en R-2026-0061 (UC nueva creada).
- `propietario [semilla] [participacion]` — Paso 2 (Cambio de Propietario): llena 'Datos
  del Nuevo Interesado' como Persona Natural con datos sinteticos UNICOS (nombre,
  documento), Sexo, Tipo Derecho Dominio, % participacion (def. 100) y pulsa 'Agregar
  Propietario'. Campos: documento/nombres/apellidos/% se llenan por POSICION (inputs
  [0]=Nº Doc, [2]=1er Nombre, [3]=2do Nombre, [4]=1er Apellido, [5]=2do Apellido,
  [6]=% number); los desplegables por opciones.
  - REGLA (OBLIGATORIO): el campo **"Autorreconocimiento étnico" debe quedar en
    "Ninguno"** (es obligatorio; sin el no se puede "Agregar Propietario"). Seleccionarlo
    SIEMPRE en los casos automaticos. No asignar etnia ficticia a datos de prueba.
  - El checkbox "Autorreconocimiento campesino" se deja SIN marcar.
  - REGLA de datos: nombres y documentos UNICOS, no repetir entre tramites.
  - **DOS MODOS de negocio (parametrizados en el comando):**
    - `MODO_SUSTITUCION_100` (`propietario <rad>`): ELIMINA el/los titular(es) previo(s)
      con la papelera `delete` y registra 1 nuevo titular al 100%. El nuevo REEMPLAZA.
    - `MODO_INCORPORACION_COPROPIEDAD` (`propietario <rad> copropiedad <n>`): NO elimina;
      agrega n copropietarios repartiendo el 100% en partes iguales (2->50/50,
      3->34/33/33). La suma SIEMPRE debe dar exactamente 100. (El ajuste del % del
      titular existente via boton Editar se hace aparte / manual si aplica.)
  - **Secuencia sustitucion:** (1) eliminar titular actual (icono papelera), (2) llenar
    'Datos del Nuevo Interesado', (3) 'Agregar Propietario'.
  - **FIX tecnico de <select>:** `select_option` por si solo NO disparaba el evento
    change de la SPA y el valor quedaba en "None" (error `2_CLLC_L76`: "Persona Natural
    con sexo None invalido"). El comando ahora dispara input+change por JS tras cada
    seleccion (helper `_select_spa`).
  - Dejar constancia de la distribucion de titulares en el resumen.txt del tramite.
  - PROBADO OK (21/10) en R-2026-0081 modo sustitucion: elimino a FRANCISCO JAVIER
    RINCON MEDELLIN y registro a LILIANA LUISA CARDENAS RIOS (CC 221558265, Femenino,
    Dominio, 100%). El fix de evento change resolvio el error de sexo None.
- `tramitepropietario [semilla] [modo] [n]` — proceso COMPLETO de Cambio de Propietario
  estando en el Paso 2: hace el cambio y AVANZA hasta el Resumen (paso 6) validando
  (lee errores/warnings/OK). NO pasa a calidad (accion critica, la confirma el usuario).
  - PROBADO OK (21/10) de punta a punta en R-2026-0082: CONSTRUCTORA BOLIVAR CALI SA
    (NIT, 0%) -> ANGELA MARCELA ZULUAGA MARTINEZ (CC 566843056, Dominio 100%). Resumen:
    0 ERRORES, 0 warnings, 51 OK. Quedo listo para 'Pasar borrador acto administrativo'
    y 'Pasar a calidad'. Titular distinto al de 0081 (datos no repetidos OK).

> ESTADO Cambios de Propietario (21/10): 0081 y 0082 CERRADOS A CALIDAD por el usuario
> (cambio de propietario + 0 errores + 'Pasar borrador' + 'Pasar a calidad'). Resumenes
> actualizados en sus carpetas (resumen_R-2026-0081.txt, resumen_R-2026-0082.txt).
> AJUSTE PENDIENTE: el comando `entrar` a veces no cambia de tramite si ya hay uno
> abierto (hay que resetear el buscador); en 0082 si cambio bien.
  - REGLA de calificacion: **CONSERVADORA** (sencillo/regular, bajo-medio puntaje). NO
    calificar alto para no inflar el avaluo ni perjudicar al propietario. Coherente con
    la info de las plantas (vivienda estandar).
  - REGLA de variacion: los datos deben VARIAR y NO repetirse entre tramites. Usar la
    semilla (radicado) para variar por tramite. PENDIENTE: dar mas variacion a la
    calificacion dentro del rango conservador (hoy usa un set fijo conservador).

> Nota mapeo Paso 3: los <select> van en grupos ciclicos. Puntos = 3 por fila
> (Tipo de punto / Metodo / Punto de control). Linderos = 2 por fila (Orientacion /
> Colinda con) + un input de texto 'NPN o nombre del colindante'.

#### Tipos de trámite que requieren intervención manual / bloquean (RESUMEN)

- **Efectos Registrales - Actualización Linderos Art. 6.1 (Mutación Integral):** muchos
  pasos son SOLO LECTURA. NO deja editar Caracterización LADM (Paso 1), Propietario
  (Paso 2), ni Construcción (Paso 4). Si la UC llega sin geometría, el Paso 7 bloquea
  con error `2_CT_CF_25` y NO hay forma de subsanar -> trámite bloqueado (#20, #21, #22).

#### Plantillas de carga masiva (carpeta `plantillas/`)

- `plantillas/plantilla_cambio_propietario.xlsx`: plantilla Excel de carga masiva con
  hojas **Instrucciones**, **Cambio_Propietario** (columnas obligatorias con `*`) y
  **Dominios** (listas de valores validos). Formato de referencia para nuevas
  plantillas.
- PENDIENTE: crear `plantillas/plantilla_topografia/plantilla_topografia.xlsx`
  (puntos + linderos) con el mismo estilo. Estructura propuesta: hoja Puntos (Nº
  radicado, NPN, Nº punto, Este, Norte, Tipo de punto, Método, Punto de control),
  hoja Linderos (Nº radicado, NPN, Tramo, Longitud, Orientación, Colinda con, NPN/
  nombre colindante) y hoja Dominios con los valores reales ya capturados. En espera
  de que el usuario confirme alcance.

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

**Sesión 16/10/2026: R-2026-0075 COMPLETADO (2 de 50).**

- R-2026-0075 (Rectificaciones - Errores Inscripción Catastral) procesado de punta a
  punta y pasado a calidad. Fue un caso rico en hallazgos (ver #4..#13).
  Correcciones que requirió: añadir dirección, editar propietario (% de 0 a 100),
  editar la UC (área 51, calificación completa, año 2016, avalúo_caracterización),
  cargar polígono de construcción (para la altura), y corregir el "Nombre" de la
  dirección estructurada original. Avalúo retroactivo desde 2016.

Para retomar la próxima vez:
1. Lanzar `uv run navegador.py` y `uv run qa.py` (dos terminales). NO abrir DevTools (F12).
2. Procesar el radicado de MENOR número en Asignado. IMPORTANTE: buscar el menor real
   entre TODAS las páginas (puede estar en la página 2), NO asumir por sesiones previas.
   Verificar en vivo con `radicados` y el buscador. (El siguiente a procesar es
   **R-2026-0072**.)

Progreso meta: **2 de 50 radicados completos** (R-2026-0077 y R-2026-0075).

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

---

### REGLA: al decir "comencemos" entregar los 2 comandos de terminal

Cuando el usuario diga "comencemos" (o similar), el agente SIEMPRE entrega de una los
DOS comandos para arrancar el entorno, listos para copiar:

Terminal 1 (navegador persistente; dejar abierta, iniciar sesion una vez, NO DevTools):
```
cd C:\Users\Jorge\Desktop\Smartcube\05_codigo
uv run python navegador.py
```

Terminal 2 (REPL de comandos):
```
cd C:\Users\Jorge\Desktop\Smartcube\05_codigo
uv run python qa.py
```

(Para el procesamiento en lote, Terminal 2 seria `uv run python lote_qa.py` en vez de qa.py.)

## 12. Para retomar (próxima sesión)

1. Lanzar el entorno (dos terminales, en `05_codigo/`):
   - `uv run python navegador.py` (dejar abierta; iniciar sesión una vez; NO abrir DevTools/F12).
   - `uv run python qa.py` (REPL de comandos).
2. **R-2026-0057:** retomar solo si el usuario resolvió el bug de plataforma (poder
   cargar la geometría de la UC). Si se puede: re-validar en el Paso 7 y pasar a calidad.
   Si no: queda bloqueado (error de origen IGAC) y se sigue con otro radicado.
3. **Revision guiada por radicado (21/10) con el comando `entrar <radicado>`:**
   - **R-2026-0061 — LISTO** (Mutacion 3a Cambio Area Construida): direccion estructurada,
     destino Habitacional, UC con calificacion conservadora, fuente admin, avaluo 2025;
     usuario resolvio los 2 errores del Paso 7. Hallazgo #23 (area grafica) en el informe.
   - **SIGUIENTE a revisar: R-2026-0062** (Mutacion 4a - Revision Avaluo). Entrar con
     `entrar R-2026-0062`, luego `paso` + `cap`. Preguntar si lleva construccion.
   - Resto del lote por revisar/completar: 0079, 0084, 0085, 0088 (avanzaron al Paso 7,
     falta geometria). 0081, 0082 (revisar, detenidos en Paso 6). 0086 (no inicio wizard).
     0067, 0087, 0089 (requieren Asignacion de NPN - cartografico).
   - Comandos de edicion disponibles: `entrar`, `editardireccion`, `destino`,
     `construccion`, `fuenteadmin`, `avaluo`, `puntosmasivo`, `linderosmasivo`, `paso`.
4. Usar los comandos de automatización del wizard (paso, puntosmasivo, linderosmasivo,
   fuenteadmin, avaluo, caracterizacion) o el lote (`lote_qa.py`). Datos sintéticos
   únicos por trámite. SIEMPRE probar con 1 radicado antes del lote.
5. PENDIENTE a pedido del usuario: crear `plantillas/plantilla_topografia/`.
6. RECORDAR la meta de **50 radicados** e informe final de inconsistencias (van 22
   hallazgos registrados). Informe base en `06_Informe/Informe_QA_SmartCube_Jamundi.docx`.

Progreso meta: **2 de 50 completos a calidad** (R-2026-0077, R-2026-0075).
R-2026-0072 en borrador; R-2026-0057 bloqueado por bug; lote 20/10 con el flujo
alfanumerico adelantado en varios (pendiente geometria del usuario).

#### Carpetas NO versionadas (fuera de git por `.gitignore`)

Son datos/entregables locales, no van al repositorio:
- `03_tramites/` — expedientes, evidencia, resumen_<RADICADO>.txt, fotos, GeoJSON.
- `06_Informe/` — informe de QA en Word (`Informe_QA_SmartCube_Jamundi.docx`).
- `plantillas/` — plantillas de carga masiva (xlsx) y `plantilla_topografia/`.
- `05_codigo/.pw-profile/`, `05_codigo/capturas/`, `05_codigo/reportes/`, `.env`.

#### Informe Word (06_Informe) — estado y REGLA de edicion

`06_Informe/Informe_QA_SmartCube_Jamundi.docx` es el informe de QA. Estructura: resumen
ejecutivo, objetivo/alcance, metodologia, clasificacion de hallazgos, hallazgos
destacados, tabla consolidada (hallazgos 1..23), recomendaciones, conclusiones, y
"Anexo A. Nota de tramite R-2026-0061" (error de area grafica del terreno 328 vs 225.73
m2, 45.3%).

ESTADO (21/10/2026): el USUARIO agrego la IMAGEN SOPORTE del Anexo A (error de area de
0061) y realizo AJUSTES MANUALES al documento. Luego se agrego de forma INCREMENTAL la
"Recomendación adicional: Implementación de subestados, bitácora interna y trazabilidad
de avance en el flujo de trámites" (subestados operativos, indicador visual de progreso
pasos 1-7, bitacora/log de intervencion, panel de seguimiento para lideres), homogenea
con las recomendaciones previas (NPN 30 digitos y copiado en linderos).

> REGLA: el informe Word tiene EDICIONES MANUALES del usuario. NO regenerarlo desde cero
> con script (se perderian sus cambios y la imagen). Si hay que agregar algo por codigo,
> hacerlo de forma INCREMENTAL (abrir el .docx existente y añadir), nunca sobrescribir.
> Preferir que el usuario haga ajustes finos a mano.

---

_Última actualización: 20/10/2026 (sesión R-2026-0057 bloqueado; comandos de
automatización del wizard agregados a qa.py)._
