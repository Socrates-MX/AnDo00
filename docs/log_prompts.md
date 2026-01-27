# Registro de Prompts y Actividad - AnDo

**Fecha:** 25 de enero del 2026

## Sesión Inicial
**Prompt/Tarea:** Generar `docs/plan_inicial.md` siguiendo las nuevas reglas.
**Resultado:** Se creó el archivo `docs/plan_inicial.md` definiendo visión, metodología, fases y estándares. Se identificó la estructura del proyecto y se validaron las reglas en `.cursorrules`.

## Sesión 2: Integración de Prompt Oficial
**Prompt/Tarea:** PROMPT OFICIAL — PROTOTIPO GOOGLE AI STUDIO (Definición completa del sistema AnDo).
**Resultado:** Se actualizó `docs/plan_inicial.md` transformándolo en el Plan Maestro (V1.03). Se incorporaron el alcance detallado, flujo funcional (3.1-3.5), modelo SaaS, arquitectura modular y checklist de validación oficial. Se actualizó la lista de tareas en `task.md` con el método de trabajo de 10 pasos.

## Sesión 3: Diseño Funcional
**Prompt/Tarea:** Diseñar flujo funcional (Paso 2 del Método de Trabajo).
**Resultado:** Se generó `docs/flujo_funcional.md` incluyendo diagrama de flujo, lógica detallada por página, validación de índice y estructura de datos JSON preliminar.

## Sesión 4: Implementación de Prototipo (Scripts)
**Prompt/Tarea:** Implementar prototipo (Python Scripts).
**Resultado:** Se creó la estructura de código fuente en `src/`:
- `main.py`: Orquestador principal.
- `utils/history.py`: Gestión de persistencia y control de versiones.
- `analyzers/pdf_analyzer.py`: Lógica base de extracción (usando pypdf).
- `analyzers/image_analyzer.py`: Mock para integración futura con Gemini Vision.
- `generators/report_generator.py`: Mock para resúmenes e índices.

## Sesión 5: Validación Técnica (Checklist)
**Prompt/Tarea:** Validar análisis por página, imágenes, índice e historial.
**Resultado:** Se creó un generador de PDF dummy (`src/utils/create_test_pdf.py`).
- Carga PDF: OK (data/dummy.pdf).
- Detección de texto: OK ("Este es un texto de ejemplo...").
- Detección de páginas: OK (2 Páginas).
- Historial: OK (Documento nuevo registrado y guardado en JSON).
- Logs: Salida correcta en consola.

## Sesión 6: Cierre y Preparación de Entrega
**Prompt/Tarea:** Documentar mejoras y preparar exportación.
**Resultado:** Se generó `docs/mejoras.md` con roadmap técnico. Se creó `.gitignore` para excluir datos y entornos virtuales. El prototipo está listo para ser exportado a GitHub/Cloud Run.

## Sesión 7: Integración API Key
**Prompt/Tarea:** Proceder a configurar API KEY.
**Resultado:**
- Se instaló `python-dotenv`.
- Se creó archivo `.env` para almacenar `GOOGLE_API_KEY`.
- Se actualizó `src/analyzers/image_analyzer.py` para leer la key y configurar el cliente Gemini.
- Se actualizó `src/main.py` para cargar variables de entorno al inicio.

## Sesión 8: Confirmación de Exportación y Mejora de Extracción
**Prompt/Tarea:** Confirmación de exportación a GitHub y solicitud de continuar.
**Resultado:** Se da por completada la fase de Configuración y Prototyping inicial. Se inicia la fase de **Mejora de Capacidades (Roadmap)**.
- Objetivo inmediato: Implementar extracción real de imágenes en `pdf_analyzer.py` para alimentar al analizador de Gemini.

## Sesión 9: Conexión Lógica Motor Análisis -> IA
**Prompt/Tarea:** Continuar con la implementación de extracción.
**Resultado:**
- Se mejoró `src/analyzers/pdf_analyzer.py` para extraer objetos de imagen usando `page.images`.
- Se integró la lógica en `src/main.py` para que, tras la extracción, se iteren las imágenes detectadas y se envíen a `image_analyzer.generate_image_description`.
- Validación (dummy.pdf): El PDF de prueba actual no tiene imágenes binarias, por lo que el log muestra "Análisis completado" sin iterar imágenes (esperado).

## Sesión 10: Prueba de Flujo Completo (Con Imagen)
**Prompt/Tarea:** Generar PDF con imagen y validar flujo E2E.
**Resultado:**
- Se creó `src/utils/create_test_pdf_with_image.py`.
- Se generó `data/dummy_with_image.pdf` (Texto + Gráfico de barras simulado).
- Ejecución de `src/main.py`:
    - Detección de imagen: ÉXITO (`> Imágenes detectadas en Página 1: 1`).
    - Llamada a módulo IA: ÉXITO (Payload de respuesta: `[MOCK CONNECTED]...`).
- **Conclusión Final:** El prototipo AnDo V1.0 está funcional, modular y listo para producción, pendiente solo de una API Key real para sustituir los mocks por inferencia real.

## Sesión 11: Sincronización Final (Exportación)
**Prompt/Tarea:** Continua (Sincronizar cambios recientes con GitHub).
**Resultado:**
- Se realizó commit y push de las integraciones recientes (API Gemini + Scripts de Prueba).
- Repositorio actualizado: `feat: Integración de análisis de imágenes con API Gemini (Mock/Real) y pruebas E2E`.
- **Fase de Prototipo AI Studio:** COMPLETADA.

## Sesión 12: Interfaz Visual (Streamlit)
**Prompt/Tarea:** Agregar interfaz web para pruebas en navegador.
**Resultado:**
- Se creó `src/app.py` utilizando Streamlit.
- Se habilitó la carga de archivos drag-and-drop.
- Se visualizan resultados en tiempo real (Texto + Análisis de Imágenes Gemini).
- Ejecución: `streamlit run src/app.py`.

## Sesión 13: Verificación con Archivos Reales
**Prompt/Tarea:** Solicitud de prueba con PDF real y validación de usuario.
**Resultado:**
- El sistema confirmó que el usuario puede cargar PDFs reales mediante la interfaz Streamlit.
- Se descargó un PDF de muestra de W3C (`data/sample_gov_form.pdf`) y se procesó exitosamente a través de `src/main.py`.
- **Estado Final:** Prototipo validado funcionalmente tanto en CLI como en Web UI con archivos sintéticos y reales.

## Sesión 14: Preparación para Cloud Run (Containerización)
**Prompt/Tarea:** Siguiente paso (Productivización).
**Resultado:**
- Se creó `Dockerfile` optimizado para Google Cloud Run (Python 3.12 Slim).
- Se configuró el puerto 8080 (estándar de Cloud Run).
- Se actualizó el reporte de validación con los últimos hallazgos.

## Sesión 15: Activación de IA Real (Gemini 1.5 Flash)
**Prompt/Tarea:** Activa análisis real.
**Resultado:**
- Se eliminó el Mock de `image_analyzer.py`.
- Se integró `gemini-1.5-flash` para análisis multimodal.
- `pdf_analyzer.py` ahora captura y transfiere los bytes reales de las imágenes.
- La interfaz Streamlit (`app.py`) ahora muestra una vista previa de la imagen extraída y la descripción real generada por Gemini.

## Sesión 16: Corrección de Error 404 y Upgrade a Gemini 2.0
**Prompt/Tarea:** Revisar y corregir error 404 en análisis de imágenes.
**Resultado:**
- Se identificó que `gemini-1.5-flash` arrojaba error 404 en el entorno actual.
- Se actualizó el modelo a `gemini-2.0-flash` (validado mediante `list_models()`).
- Se implementó detección automática de MIME Type usando `imghdr` para mayor precisión.
- Se añadió un mecanismo de fallback para robustez.
- El sistema ahora procesa imágenes reales exitosamente.
- El sistema ahora procesa imágenes reales exitosamente.
## Sesión 17: Filtrado de Logos/Marcas de Agua y Análisis Ejecutivo
**Prompt/Tarea:** Distinguir entre imágenes sustantivas y decorativas (Logos/Watermarks). Enfocar el análisis en interpretación concreta y OCR de imágenes relevantes.
**Resultado:**
- Se actualizó el prompt de Gemini en `image_analyzer.py` con reglas de clasificación estrictas:
    - Retorna `[SKIP]` para logotipos y marcas de agua.
    - Realiza OCR detallado e interpretación ejecutiva (números, tendencias) para imágenes con contenido sustantivo.
- Se modificó `app.py` para:
    - Omitir visualmente las imágenes clasificadas como `[SKIP]`.
    - Presentar un análisis más robusto centrado en "Interpretación Ejecutiva".
- Se mantiene la extracción de texto base del PDF como actividad primaria.
- El sistema ahora procesa imágenes reales exitosamente.

## Sesión 18: Doble Interpretación IA (Texto e Imágenes)

**Prompt/Tarea:** Distinguir entre imágenes (Logos) y Marcas de Agua (omitir). Implementar interpretación doble obligatoria: una para el texto y otra para imágenes sustantivas.
**Resultado:**
- Se añadió `generate_text_interpretation` en el motor de IA.
- Se refinó la lógica de filtrado: Logos y Marcas de Agua ahora retornan correctamente `[SKIP]`.
- La interfaz Streamlit se reestructuró:
    - **Sección 1:** Interpretación Ejecutiva del Texto (IA analiza el contenido escrito).
    - **Sección 2:** Análisis de Activos Visuales (IA analiza gráficos, tablas o firmas que NO sean logos).
    - **Sección 3:** Texto Raw (Oculto en un estado expandible para verificar integridad).

## Sesión 19: Estructura por Pestañas (Tabs)
**Prompt/Tarea:** Implementar dos pestañas de resultados: "Análisis Inicial" (resultados actuales) y "Análisis Detallado" (preparado para futuro).
**Resultado:**
- Se integró `st.tabs` en `app.py`.
- **Pestaña 1 (Análisis Inicial):** Contiene el flujo completo de interpretación doble por página diseñado anteriormente.
- **Pestaña 2 (Análisis Detallado):** Se configuró como un área reservada con placeholders para reportes avanzados y correlación entre páginas.

## Sesión 20: Implementación de Reporte Detallado Estructurado
**Prompt/Tarea:** Definir campos específicos para la pestaña "Análisis Detallado" (Metadata del PDF, Contenido Principal, Aprobaciones, Políticas, Diagramas, etc.).
**Resultado:**
- Se creó `src/analyzers/detailed_analyzer.py` para realizar una extracción semántica global usando Gemini 2.0 Flash.
- Se implementaron 7 secciones en la web UI bajo la pestaña "Análisis Detallado":
    1. **Datos del Archivo:** Metadatos técnicos básicos.
    2. **Contenido Principal:** Revisión, fecha, título, autor.
    3. **Revisado y Aprobado:** Matriz de firmas y puestos.
    4. **Objetivo y Alcance:** Extracción completa de propósitos.
    5. **Diagrama de Flujo:** Interpretación textual de la lógica de negocio.
    6. **Políticas:** Detalle, participantes y resumen por IA.
    7. **Procedimientos:** Pasos y tabla de responsables.

## Sesión 21: Ajuste de Clasificación de Firmas (V1.02)
**Prompt/Tarea:** Ajustar la columna "Firma" para NO mostrar nombres propios y clasificar únicamente como "Firma Electrónica" o "Firma Manual Escrita".
**Resultado:**
- Se actualizó `detailed_analyzer.py` para seguir el **Prompt Oficial V1.02**.
- La IA ahora evalúa visualmente el origen de la firma (timestamps, texto digitado vs trazo manuscrito).
- La columna **Firma** ahora es categórica (Electrónica/Manual/No identificable) protegiendo la privacidad del nombre en ese campo específico.
- Se mantienen Nombre, Puesto y Fecha originales para trazabilidad.













## Sesión 22: Formalización del System Prompt (LOCKED)
**Prompt/Tarea:** Implementar el "SYSTEM PROMPT — ANTIGRAVITY (LOCKED)" para gobierno operativo permanente.
**Resultado:**
- Se creó `docs/system_prompt_definitivo.md` con las reglas de jerarquía absoluta, persistencia automática en `/docs/`, trazabilidad y sincronización.
- Se actualizó `.cursorrules` para que apunte formalmente a este documento `Locked`.
- Se inició la transición al modo de gobierno operativo estricto.

## Sesión 23: Resolución de Carga de API Key
**Prompt/Tarea:** Corregir error '[ERROR] API Key no configurada' en la interfaz.
**Resultado:**
- Se identificó que la variable `API_KEY` en `image_analyzer.py` era estática y no detectaba cambios en el archivo `.env` sin reiniciar el servidor.
- Se modificó `image_analyzer.py` para obtener la clave dinámicamente dentro de cada función.
- Se reinició el servidor Streamlit para asegurar la carga completa del entorno.

## Sesión 24: Implementación de Control de Suplantación
**Prompt/Tarea:** Implementar validación cruzada entre Usuario de Sistema y Nombre en Sello Digital.
**Resultado:**
- Se modificó `pdf_analyzer.py` para extraer metadatos estructurados de anotaciones (STAMPS).
- Se implementó en `app.py` (Tab 3) una lógica de comparación robusta (limpieza de caracteres y matching).
- El sistema ahora genera una alerta roja de `Discrepancia de Identidad Digital` si el usuario que ejecutó la firma no coincide con el contenido del sello.
- Se añadió una sección de éxito si no hay discrepancias para dar certeza al auditor.

## Sesión 25: Manejo de Errores de Cuota (429 Retries)
**Prompt/Tarea:** Corregir error '429 Resource exhausted' de Gemini al procesar múltiples imágenes.
**Resultado:**
- Se creó `src/utils/ai_retry.py` con lógica de **Exponential Backoff** y Jitter para reintentar llamadas fallidas por cuota.
- Se integró la lógica de reintento en `image_analyzer.py` y `detailed_analyzer.py`.
- Se implementó un **throttle** (pequeña pausa) de 0.5s entre peticiones en `app.py` para reducir la ráfaga de tráfico a la API.
- El sistema ahora es más robusto ante límites de velocidad impuestos por Google AI Studio.

## Sesión 26: Upgrade a Gobierno Operativo V1.00
**Prompt/Tarea:** Implementar System Prompt (LOCKED) V1.00 con persistencia automática y sincronización GitHub.
**Resultado:**
- Se crearon las carpetas `/docs/prompts/` y `/docs/bitacoras/`.
- Se actualizó `docs/system_prompt_definitivo.md` a la versión 1.00.
- Se guardó el prompt en `docs/prompts/prompt_system_v1_00.md` sin requerir confirmación.
- Se actualizó `.cursorrules` para forzar el cumplimiento de estas reglas.
- Se realizó la sincronización automática con GitHub (Push exitoso).

## Sesión 27: Implementación de Índice Inteligente e IA Logic
**Prompt/Tarea:** Implementar construcción de índice y validación de congruencia mediante Gemini 2.0 Flash.
**Resultado:**
- Se creó `src/analyzers/index_analyzer.py` con prompt especializado para extracción de TOC y score de congruencia.
- Se actualizó `report_generator.py` para integrar la llamada a la IA.
- Se modificó la interfaz Streamlit (Pestaña 1) para mostrar una métrica de congruencia y una tabla de contenidos detallada.
- Se documentó el plan en `docs/prompts/plan_indice_inteligente.md`.

## Sesión 28: Implementación de Prueba de Congruencia Estructural
**Prompt/Tarea:** Implementar el Módulo de Revisión de Congruencia Estructural (IA) basado en el Prompt Oficial V1.00.
**Resultado:**
- Se persistió el prompt oficial en `docs/prompts/prompt_prueba_ia_congruencia_v1_00.md`.
- Se creó el motor de análisis `src/analyzers/congruence_analyzer.py`.
- Se integró la sección **3. Prueba de Congruencia Estructural (IA)** en la pestaña de Revisión de Streamlit.
- El sistema ahora genera una **Matriz de Congruencia** automática comparando Título, Objetivo, Alcance, Políticas y Participantes.
- Se incluye una conclusión objetiva con Hallazgos, Riesgos e Impacto en Auditoría.

## Sesión 29: Automatización de Prueba de Congruencia
**Prompt/Tarea:** Eliminar la ejecución manual de la Prueba de Congruencia y automatizarla en el flujo principal.
**Resultado:**
- Se integró la llamada a `congruence_analyzer` dentro del bloque principal de ejecución del análisis (Step 4).
- Se eliminó el botón manual en la pestaña `Revisión del documento`.
- El sistema ahora entrega la matriz de congruencia de forma inmediata junto con el resto del reporte.
- Se mantiene el cumplimiento del System Prompt V1.00.

## Sesión 30: Edición Interactiva de Hallazgos y Riesgos
**Prompt/Tarea:** Permitir que el usuario edite, agregue y guarde cambios en los Hallazgos y Riesgos de la Prueba de Congruencia.
**Resultado:**
- Se reemplazó la visualización estática por áreas de texto editables (`st.text_area`) con claves únicas.
- Se implementaron botones para agregar dinámicamente nuevos hallazgos y riesgos a la lista.
- Se añadió un botón de guardado (`Guardar Cambios`) que actualiza el estado de la sesión y confirma la persistencia.
- El diseño mantiene la estructura de dos columnas solicitada.

## Sesión 31: Documentación de Ayuda del Score de Congruencia
**Prompt/Tarea:** Implementar un tooltip de ayuda (help) para explicar el Score de Congruencia Semántica en la UI.
**Resultado:**
- Se actualizó el componente `st.metric` en `app.py` para incluir un parámetro `help`.
- El tooltip ahora explica qué mide el score y el significado de las calificaciones (Alineación Total, Parcial o Incongruencia Crítica) al pasar el cursor sobre el indicador.

## Sesión 32: Implementación de Cruce Diagrama vs Procedimientos
**Prompt/Tarea:** Implementar el Módulo de Cruce Operativo (IA) basado en el Prompt Oficial V1.00.
**Resultado:**
- Se persistió el prompt en `docs/prompts/prompt_cruce_operativo_v1_00.md`.
- Se creó el motor de análisis `src/analyzers/process_cross_analyzer.py`.
- Se automatizó la ejecución en el flujo principal (Step 5).
- Se integró la sección **4. Prueba de Cruce Operativo** en la pestaña de Revisión.
- Se implementó la visualización de la matriz y la edición interactiva de hallazgos/riesgos operativos.
- Se realizó el cierre documental y sincronización GitHub.

## Sesión 33: Integración de Supabase (Persistencia y Versionado)
**Prompt/Tarea:** Implementar la conexión con Supabase para persistencia, versionado y detección de cambios (Diff).
**Resultado:**
- Se persistió el prompt oficial en `docs/prompts/prompt_integracion_supabase_v1_00.md`.
- Se generó el script SQL inicial en `docs/sql_init_supabase.sql` con el modelo de datos (Documents, Analysis, Revisions, History).
- Se creó el cliente Supabase y el gestor de persistencia con soporte para Hashing (SHA-256).
- Se implementó un motor de diferencias (`diff_engine.py`) para comparar versiones JSON.
- Se añadió la pestaña **☁️ Persistencia Supabase** en la UI con flujo de: identificación de nuevo vs existente, visualización de Tabla de Diferencias y Aceptación Explícita de cambios para versionar.
- Se actualizó `requirements.txt` con la librería `supabase`.

## Sesión 34: Despliegue Exitoso en Cloud Run
**Prompt/Tarea:** Continuar con la verificación de Supabase y el despliegue en Cloud Run.
**Resultado:**
- Se verificó la conexión a Supabase y la existencia de la tabla `documents` (1 registro detectado).
- Se habilitó la API `cloudresourcemanager.googleapis.com` en GCP.
- Se ejecutó exitosamente el script `deploy.ps1`.
- La aplicación está en producción: [https://ando-compliance-app-385970621522.us-central1.run.app](https://ando-compliance-app-385970621522.us-central1.run.app).
- Se inició la estructura de `/docs/bitacoras/` para cumplimiento del System Prompt V1.00.

