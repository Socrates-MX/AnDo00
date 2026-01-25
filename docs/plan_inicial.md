# Plan Maestro: Prototipo AnDo (Analizador de Documentos)

**Fecha:** 25 de enero del 2026
**Responsable:** Ingeniero Líder GetAuditUP
**Estado:** Planificación Inicial

---

## 1. Objetivo del Sistema
Diseñar y construir un **prototipo funcional SaaS** denominado **Analizador de Documentos (AnDo)** para analizar PDFs, extraer contenido estructurado (texto e imágenes), generar tarjetas de análisis, índices inteligentes, y resúmenes ejecutivos con IA. El prototipo se desarrollará inicialmente simulando un entorno **Google AI Studio** y se preparará para su exportación a **Google Cloud Run**.

## 2. Alcance Funcional

### 2.1 Incluido (Scope)
*   **Análisis PDF:** Carga, conteo de páginas, extracción de texto e imágenes.
*   **Tarjetas por Página:** Generación de contenido estructurado por página.
*   **Imágenes:** Detección y conversión IA a texto descriptivo.
*   **Índice Inteligente:** Construcción de índice y validación de congruencia (Título vs Contenido) mediante IA.
*   **Resumen Ejecutivo:** Síntesis final con hallazgos y naturaleza del documento.
*   **Historial:** Registro de análisis con fecha/hora (Formato: "25 de enero del 2026", 24h).
*   **Modelo SaaS:** Simulación de consumo de créditos.
*   **UX/UI:** Diseño sobrio y empresarial (Interfaz por tarjetas).

### 2.2 Excluido (No-Go)
*   Código final productivo (frontend/backend complejo).
*   Modificación de configuraciones existentes de GetAuditUP.
*   Eliminación de historiales.
*   Lógica de facturación real.

## 3. Flujo Funcional (Workflow)
1.  **Carga:** Usuario sube PDF -> Validación formato/tamaño -> Registro historial.
2.  **Análisis por Página:** Iteración página a página -> Extracción texto -> Descripción imágenes -> Generación Tarjeta.
3.  **Índice:** Identificación estructura -> Validación cruzada IA (Título vs. Contenido real).
4.  **Resumen:** Generación de reporte ejecutivo final.
5.  **Persistencia:** Guardado de resultados (Simulado en archivos locales/JSON por ahora).

## 4. Arquitectura del Prototipo (Python Modular)
El desarrollo se realizará en Python, estructurado para ser portable a Cloud Run.

*   `/src/main.py`: Orquestador principal.
*   `/src/analyzers/pdf_analyzer.py`: Lógica `pypdf`/`pdfplumber`.
*   `/src/analyzers/image_analyzer.py`: Lógica de extracción y mock de llamada a IA (o llamada real si API Key disponible).
*   `/src/generators/report_generator.py`: Construcción de resumen y JSON final.
*   `/src/utils/history.py`: Gestión de logs y persistencia local.

## 5. Checklist de Validación
- [ ] PDF cargado correctamente.
- [ ] Conteo correcto de páginas.
- [ ] Tarjeta creada por cada página.
- [ ] Imágenes analizadas y convertidas a texto.
- [ ] Índice generado correctamente.
- [ ] Congruencia índice vs contenido validada.
- [ ] Historial registrado correctamente.
- [ ] Revisión con cambios funcional.
- [ ] Revisión completa funcional.
- [ ] Resumen ejecutivo generado.
- [ ] Diseño sobrio y ejecutivo.
- [ ] Arquitectura abierta a mejoras.

## 6. Próximos Pasos (Hoja de Ruta)
1.  Diseñar el flujo funcional detallado (`docs/flujo_funcional.md`).
2.  Implementar scripts base de Python para extracción de PDF.
3.  Integrar (simular) análisis de imágenes e índice.
4.  Ejecutar validaciones.

---
© 2026 Analizador de Documentos. Empowered by FMConsulting V1.03
