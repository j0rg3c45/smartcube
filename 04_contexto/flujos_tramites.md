# Flujos de tramites SmartCube - Referencia unica

Documento de referencia del proceso de QA de la plataforma catastral SmartCube
(Jamundi). Centraliza el flujo base del wizard y las variaciones por tipo de
mutacion, para no repetir la logica en cada tramite.

Arquitectura de operacion (MODO AUTONOMO desde 04/11/2026): el usuario deja abierto
`navegador.py` (Chrome CDP 9222) y el AGENTE ejecuta el mismo, por shell, scripts
temporales en `05_codigo/` que hacen `import qa` y se conectan al mismo Chrome:

    cfg = qa.cargar_config(); qa._pedir_confirmacion = False
    p, browser, page = qa.conectar(cfg)

Ejecucion: `$env:PYTHONIOENCODING='utf-8'; uv run python _tmp_x.py > _tmp_out.txt 2>&1`
y leer `_tmp_out.txt`. Borrar los temporales al terminar. El agente no pide
confirmacion para navegar, iniciar tramites ni diligenciar; solo pausa ante la
geometria con el mensaje estandar `[PAUSA CARTOGRAFICA] Tramite [RAD]: ...`. Los
radicados se procesan EN ORDEN (menor numero primero). La cartografia (geometria de
terreno y construcciones) queda SIEMPRE reservada para el usuario.

Lanzamiento (desde `05_codigo/`, gestor uv):
- Terminal 1: `uv run python navegador.py`  (Chrome CDP persistente, puerto 9222)
- Terminal 2: `uv run python qa.py`          (REPL de comandos)
- Verificar navegador vivo: `Invoke-WebRequest http://localhost:9222/json/version`

Reglas transversales (aplican a todos los tramites):
- Datos sinteticos UNICOS, no repetidos entre tramites (nombres, documentos,
  direcciones). Direccion siempre Estructurada; reusar numeros del origen si existen.
- Calificacion de construccion CONSERVADORA (sencillo/regular), variada por semilla.
- Geometria = reserva del usuario. El agente solo llena lo alfanumerico.
- "Pasar a calidad" / "Pasar borrador acto administrativo" son ACCIONES CRITICAS:
  las confirma y pulsa el USUARIO. Nunca automatico.
- Al cerrar cada tramite, generar `resumen_<RADICADO>.txt` en
  `03_tramites/NN_tramite_<RADICADO>/`.
- Codigo sin tildes ni emojis. Informe Word SI con tildes y sin borrar imagenes.

---

## Bloque base compartido (pasos 1 a 7)

| Fase | Accion base (igual para casi todos) | Notas / gotchas |
|------|-------------------------------------|-----------------|
| 0. Rotulo | Leer SIEMPRE el rotulo del tramite antes de actuar. | Detecta mixtas/integrales y numero de etapas. No asumir flujo simple. |
| 1. Predio | Caracterizacion LADM + Direccion Estructurada unica + Destino economico coherente. | Si el predio tiene construccion y viene como "Lote Urbanizado No Construido", cambiar el destino a uno edificado (Habitacional por def.) o el Paso 7 marca CUSTOM_DESTINO_REQUIERE_UC. |
| 2. Propietario | Datos sinteticos unicos; Persona Natural con nombre+apellido+sexo; % Dominio = 100 (propietario unico). | El % suele llegar en 0 (hallazgo recurrente); corregir a 100. El sexo suele llegar en None; asignarlo. |
| 3. Terreno | Geometria = usuario. El agente solo avanza/valida. | Tras cargar el terreno pueden aparecer traslapes con vecinos (CUSTOM_TERRENO_TRASLAPE_VECINO, FIJA_TRASLAPE_COLINDANTE); los resuelve el usuario. El area (3_ET_CF_108) se concilia cargando el terreno. |
| 4. Construccion | Geometria = usuario. El agente edita la calificacion catastral (16 desplegables) conservadora y variada. | Elegir Tipo unidad (Residencial...) y Uso ANTES de que aparezcan los desplegables. La altura/planta sale de la geometria, no se digita. |
| 5. Fuente administrativa | 7 desplegables + numeros/fechas/observacion. | Los 7 selects pueblan sus opciones de forma ASINCRONA: esperar a que haya opciones antes de seleccionar. Valores fijos: Escritura Publica / Valle del Cauca / Jamundi. NO pulsar "Agregar fuente": crea una 2a fuente vacia que bloquea "Siguiente Paso" sin aviso (si pasa, "Eliminar" la 2a). |
| 6. Avaluo | Retroactivo, por defecto 2025. | Cambio de propietario puede NO tener este paso. |
| 7. Resumen | Re-validar hasta 0 errores. | Si hay errores, corregir y re-validar. Al quedar en 0, el usuario decide pasar a calidad. |
| Cierre | Generar `resumen_<RADICADO>.txt`. | — |

Gotchas generales (04/11/2026):
- Tour de novedades (MULTICAT, "Paso 1 de 4"): su overlay intercepta todos los clics.
  Llamar `qa.cerrar_tour(page)` al entrar y en cada paso (ya lo hacen
  `continuar_wizard` y `tramite_auto`).
- Las pestanas de pasos (1. PREDIO ... 8. BORRADOR) estan deshabilitadas: navegar solo
  con Anterior / Siguiente Paso.
- Antes de leer el conteo del Resumen usar `qa.esperar_validaciones(page)`.
- Predio existente (Revision Avaluo, Rectificaciones, 3a): `tramite_auto(page, sem,
  "2025", "conservar")` no toca caracterizacion ni destino; `editar_todas_uc` completa
  lo alfanumerico de todas las UC.
- `qa.entrar_radicado(page, cfg["url"], "R-2026-XXXX")` (base_url primero).

Comando motor base: `tramiteauto [semilla] [anio]` recorre el wizard de forma
auto-adaptativa (inspeccion dinamica del DOM) hasta el Resumen; sirve para tipos
nuevos o atipicos. Comandos por paso: `caracterizacion`, `editardireccion`,
`destino`, `construccion`, `fuenteadmin`, `avaluo`, `validar`, `continuar`, `paso`,
`cap`, `selects`.

---

## Modulos de variacion por tipo de tramite

| Tipo de mutacion | Rama especifica | Comando(s) |
|------------------|-----------------|-----------|
| Cambio de propietario | Sustitucion: eliminar el titular previo (papelera "delete" + aceptar modal) y registrar nuevo al 100%. Copropiedad: no elimina, reparte % entre N. | `propietario [sem] [modo] [n] [sexo]`, `tramitepropietario [sem] [modo] [n] [sexo]` (hace el cambio y avanza hasta Resumen). sexo = femenino/masculino (opcional). |
| Cancelacion por fuerza mayor | Justificacion de evento natural + fuente administrativa. | `cancelacion [semilla]` |
| Mutacion 3a (cambio area / cambio destino) | Parte 1 hasta Paso 4 (usuario sube geometria de construccion); parte 2 edita calificacion UC + avaluo + resumen. Propietario de SOLO LECTURA (puede venir en 0%, no corregible). Errores tipicos que quedan al usuario: 2_CLUC_CF_81 (altura) y 3_ET_CF_108 (area). | `tramite3a [sem] [destino]` + `tramite3afin [sem] [anio]`; en modo autonomo: direccion + `editar_todas_uc` + fuente + avaluo (ver R-2026-0238). |
| Mutacion 4a Revision Avaluo | Predio existente: modo `conservar`, editar todas las UC, avaluo retroactivo. Puede salir CUSTOM_AVALUO_COMPLETO "sin valor en tabla" (hallazgo 29). | `tramite_auto(..., "conservar")` + `editar_todas_uc` |
| Mutacion mixta / integral | Leer el rotulo: son 2+ mutaciones en orden que salen en UNA resolucion. Procesar Etapa 1, "Guardar etapa y continuar", luego Etapa 2. Cada etapa es su propio wizard. | Comandos del tipo de cada etapa (p. ej. Etapa 1 Rectificacion + Etapa 2 `tramitepropietario`). |
| Mutacion 2a (division / segregacion) y Rectificacion Cambio NPN | Requieren Asignacion de NPN (geometria) ANTES del wizard. El primer paso lo hace el usuario (cartografia). | Asignacion de NPN manual -> luego flujo base. |
| Efectos Registrales | Caso especial; pasos obligatorios no editables. R-2026-0057 quedo BLOQUEADO por UC sin geometria de origen (bug IGAC). | — |

---

## Estados y limites

- Iniciar el wizard y avanzar pasos NO cambia el estado del radicado (sigue
  "Asignado"); solo "Pasar a calidad" lo saca de Asignacion.
- El agente se detiene e informa ante: error critico, modal inesperado, fallo de
  sesion/red, o paso que exige geometria (reserva del usuario).
- Entregable final del proceso: al llegar a 50 radicados, informe profesional con
  todas las inconsistencias registradas (una por hallazgo: radicado, campo,
  descripcion, evidencia).
