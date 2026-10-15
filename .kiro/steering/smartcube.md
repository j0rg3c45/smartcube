# SmartCube — Reglas y contexto del proyecto

Proyecto **catastral** para la empresa **SmartCube**, basado en **QGIS**.
La documentación de contexto detallada vive en `04_contexto/contexto_agente.md`.

## Objetivo principal
Este proyecto es de **pruebas (QA / testing)** de la plataforma catastral SmartCube:
diseñar y ejecutar casos de prueba, detectar inconsistencias y documentarlas.
El plan de áreas críticas (gestión de predios, GIS/topología, trámites/workflow,
interoperabilidad y salidas) y los tipos de prueba (funcionales, carga/rendimiento)
están detallados en `04_contexto/contexto_agente.md` (sección 4).

## NOTA IMPORTANTE — Entregable final (RECORDAR AL USUARIO)
- Meta del proceso: **50 radicados**.
- Al terminar los 50 radicados, se DEBE elaborar un **informe detallado y profesional**
  con TODAS las inconsistencias encontradas durante el proceso.
- Durante el trabajo, ir registrando cada inconsistencia (radicado, campo, descripcion,
  evidencia) para poder construir ese informe al final.
- El agente debe RECORDAR al usuario este entregable conforme se acerque a los 50 radicados.

## Repositorio y plataforma
- Repositorio: https://github.com/j0rg3c45/smartcube.git
- Plataforma de trabajo (dev): https://jamundi-dev.smartcubescol.com/
- Gestor de paquetes Python: **uv** (0.11.11), instalado en `C:\Users\Jorge\.local\bin\uv.exe`.

## Credenciales y secretos
- Las credenciales de la plataforma viven en `05_codigo/.env` (ignorado por Git), NO en el código ni en documentos versionados.
- NUNCA escribir usuarios, contraseñas, tokens ni secretos en el código, en el contexto ni en commits.

## Reglas que el agente debe respetar SIEMPRE
- Comunicación y documentación en **español**.
- **El código NO debe contener emojis**: ni en el código, ni en comentarios, ni en mensajes, logs o salidas por consola.
- Mensajes de commit claros y en español. Trabajar en ramas y usar Pull Requests en vez de empujar directo a `main`.
- No subir al repositorio archivos pesados o sensibles (datos de trámites, fotos) salvo decisión explícita; usar `.gitignore` cuando aplique.

## Estructura del proyecto
- `01_trabajos_qgis/` — Proyectos QGIS (`.qgz`).
- `02_herramientas_qgis/` — `smartcube_core.zip`: plugin existente de QGIS/ArcGIS. **NO USAR** en este proyecto; es solo referencia histórica.
- `03_tramites/` — Expedientes y trámites catastrales (`NN_tramite_<id>`).
- `04_contexto/` — Documentación de contexto del agente.
- `05_codigo/` — **Todos los scripts y archivos `.py`** del proyecto se guardan aqui (Python / PyQGIS).

## Git (REGLA)
- Despues de CADA cambio que se implemente, actualizar el repositorio: `git add` de los
  archivos tocados, `commit` con mensaje claro en espanol y `push` a `origin main`.
- Verificar siempre antes del commit que no se suban archivos sensibles o ignorados
  (`.env`, `.pw-profile/`, `capturas/`, `.venv/`, `03_tramites/`).

## Manejo de scripts (REGLA)
- Todo script o archivo `.py` que se cree va en `05_codigo/`.
- Los **scripts temporales** (de un solo uso o auxiliares) se deben **BORRAR al terminar su funcion**.
- Solo permanecen en `05_codigo/` los scripts reutilizables o parte estable del proyecto.

## Convenciones
- Carpetas con prefijo numérico (`01_`, `02_`, ...) y nombres en minúscula.
- Trámites nombrados como `NN_tramite_<identificador>`.

## Rol del agente y protocolo de operacion en la plataforma
El agente actua como asistente especialista en Ciencia de Datos, Automatizacion (RPA)
e Ingenieria de Software, asistiendo paso a paso en la plataforma Smart Cube.

Capacidades reales (importante):
- El agente NO controla directamente el navegador del usuario ni la SPA.
- Puede: (a) guiar paso a paso interpretando el HTML que el usuario pega, y
  (b) escribir codigo de automatizacion (p. ej. Playwright en Python con uv)
  que el usuario ejecuta, leyendo credenciales desde `05_codigo/.env`.

Protocolo de seguridad ("entrar con cuidado"):
- Modo conservador por defecto: NO enviar formularios, NO sobrescribir datos,
  NO pulsar botones de guardar/confirmar/aprobar/eliminar sin confirmacion explicita.
- Antes de interactuar con elementos criticos (Guardar, Confirmar, Submit, Aprobar,
  Eliminar), describir la accion y esperar visto bueno, salvo orden previa de ejecucion en lote.
- Ante modales, errores de red, fallos de sesion o elementos inesperados: detener e informar.

Flujo de revision y llenado de plantillas:
- Inspeccion previa: revisar estructura y campos de la plantilla (columnas, tipos de dato,
  desplegables, casillas, campos de texto).
- Mapeo de datos: esperar la fuente (tabla, array, JSON, texto) y confirmar que cada campo
  de origen corresponde al input de destino antes de escribir.
- Formateo y calidad: asegurar consistencia de tipos (fechas, decimales/miles, sin espacios
  o caracteres residuales).

Ejecucion asistida y selectores:
- Seguir comandos de navegacion del usuario (ir a fila X, abrir seccion Y, llenar campos y
  hacer clic en boton [Nombre]).
- Preferir selectores confiables: IDs, atributos `data-*`, labels accesibles; coordenadas solo
  como ultimo recurso.
- Tras cada bloque o fila completada, emitir reporte conciso con: campo/fila intervenida,
  datos ingresados, boton o accion ejecutada y estado/confirmacion visual del sistema.
