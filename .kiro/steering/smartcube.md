# SmartCube — Reglas y contexto del proyecto

Proyecto **catastral** para la empresa **SmartCube**, basado en **QGIS**.
La documentación de contexto detallada vive en `04_contexto/contexto_agente.md`.

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
- `05_codigo/` — Código fuente (Python / PyQGIS).

## Convenciones
- Carpetas con prefijo numérico (`01_`, `02_`, ...) y nombres en minúscula.
- Trámites nombrados como `NN_tramite_<identificador>`.
