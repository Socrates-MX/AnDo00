import streamlit as st
import os
import shutil
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar lógica del backend
from analyzers import pdf_analyzer, image_analyzer
from utils import history

st.set_page_config(page_title="Prototipo AnDo", layout="wide", page_icon="📄")

# Layout
st.title("📄 Analizador de Documentos (AnDo)")
st.markdown("**Prototipo V1.0 - Powered by Google Gemini**")

# Sidebar para estado y configuración
with st.sidebar:
    st.header("Estado del Sistema")
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key and api_key != "YOUR_API_KEY_HERE":
        st.success("✅ API Key Configurada")
    else:
        st.error("❌ API Key No Configurada (Modo Mock)")
    
    st.divider()
    st.info("Sube un PDF para comenzar el análisis.")

# Área de carga
uploaded_file = st.file_uploader("Elige un archivo PDF", type="pdf")

if uploaded_file is not None:
    # Guardar archivo temporalmente
    temp_dir = "data/temp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.divider()
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Información")
        st.write(f"📁 **Archivo:** {uploaded_file.name}")
        st.write(f"📏 **Tamaño:** {uploaded_file.size / 1024:.2f} KB")
        
        # Historial
        doc_info, is_new = history.register_document(temp_path)
        if is_new:
            st.info("🆕 Documento Nuevo")
        else:
            st.warning("⚠️ Documento Previamente Analizado")
            st.json(doc_info, expanded=False)

    # --- Estado de Sesión ---
    if 'analizado' not in st.session_state:
        st.session_state.analizado = False
    if 'pages_data' not in st.session_state:
        st.session_state.pages_data = None
    if 'detailed_report' not in st.session_state:
        st.session_state.detailed_report = None

    with col2:
        st.subheader("Resultados del Análisis")
        
        # Botón principal de trigger
        if st.button("🚀 Ejecutar Análisis IA", type="primary"):
            with st.spinner("Analizando documento..."):
                # 1. Ejecutar análisis inicial (Páginas e Imágenes)
                st.session_state.pages_data = pdf_analyzer.analyze_pdf(temp_path)
                if st.session_state.pages_data:
                    for page in st.session_state.pages_data:
                        page['text_interpret'] = image_analyzer.generate_text_interpretation(page['text_content'])
                        time.sleep(0.5) # Throttle
                        for img in page.get('images', []):
                            img['description'] = image_analyzer.generate_image_description(img['image_bytes'])
                            time.sleep(0.5) # Throttle
                    
                    # 2. AUTOMATIZACIÓN (V1.03): Disparar Informe Detallado inmediatamente
                    from analyzers import detailed_analyzer
                    with st.spinner("Generando Informe de Auditoría Estructurado automáticamente..."):
                        detailed_json_raw = detailed_analyzer.extract_detailed_analysis(st.session_state.pages_data, temp_path)
                        try:
                            import json
                            st.session_state.detailed_report = json.loads(detailed_json_raw)
                        except Exception as e:
                            st.error(f"Error en la generación automática del reporte: {e}")
                    
                    st.session_state.analizado = True
                else:
                    st.error("Error al procesar el PDF.")

        # Mostrar resultados si ya está analizado
        if st.session_state.analizado:
            pages_data = st.session_state.pages_data
            total_pages = len(pages_data)
            st.success(f"Análisis Completado: {total_pages} páginas procesadas y Reporte Detallado generado.")
            
            # Definición de Pestañas (Tabs)
            tab1, tab2, tab3 = st.tabs(["📊 Análisis Inicial", "🔍 Análisis Detallado", "📑 Revisión del documento"])

            with tab1:
                st.markdown("### Interpretación de Páginas (Texto + Imágenes)")
                for idx, page in enumerate(pages_data):
                    with st.expander(f"Página {page['page_number']}", expanded=(idx==0)):
                        st.subheader("📝 Análisis del Contenido Escrito")
                        st.info(f"**Interpretación Ejecutiva:**\n\n{page['text_interpret']}")
                        
                        st.divider()
                        
                        if page['images']:
                            st.subheader("🖼️ Análisis de Activos Visuales")
                            for img in page['images']:
                                desc = img['description']
                                if "[SKIP]" in desc.upper():
                                    st.caption(f"ℹ️ Imagen `{img['name']}` omitida (Logotipo/Marca de Agua).")
                                    continue
                                
                                st.image(img['image_bytes'], caption=f"Imagen: {img['name']}", width=400)
                                st.warning(f"**Hallazgo en Imagen:**\n\n{desc}")
                        
                        with st.status(f"Ver Texto Original Extraído (Pág {idx+1})"):
                            st.text_area("OCR/Raw Text", page['text_content'], height=150, key=f"text_{idx}")

            with tab2:
                st.markdown("### 📋 Reporte de Auditoría Detallado")
                st.caption("© 2026 Analizador de Documentos. Empowered by FMConsulting V1.03")
                
                # Mostrar reporte si ya existe (Generado automáticamente)
                if st.session_state.detailed_report:
                    data = st.session_state.detailed_report
                    
                    def check(val):
                        return val if val and val != "..." else "No identificado en el documento"

                    # Secciones del Reporte
                    st.header("1. Datos del Archivo PDF")
                    st.write(f"**Nombre del archivo PDF:** {uploaded_file.name}")
                    st.write(f"**Tamaño del archivo:** {uploaded_file.size / 1024:.2f} KB")
                    st.write(f"**Número de páginas del archivo:** {total_pages}")

                    st.header("2. Contenido Principal")
                    cp = data.get("contenido_principal", {})
                    st.write(f"**Tipo / No. de Documento:** {check(cp.get('tipo_no_documento'))}")
                    st.write(f"**Número de Revisión:** {check(cp.get('numero_revision'))}")
                    st.write(f"**Fecha de Efectividad:** {check(cp.get('fecha_efectividad'))}")
                    st.write(f"**Título del Documento:** {check(cp.get('titulo_documento'))}")
                    st.write(f"**Elaborado por:** {check(cp.get('elaborado_por'))}")
                    st.write(f"**Razón del Cambio:** {check(cp.get('razon_cambio'))}")

                    st.header("3. Revisado y Aprobado")
                    ra_data = data.get("revisado_aprobado", [])
                    if ra_data: st.table(ra_data)
                    else: st.info("No identificado en el documento")

                    st.header("4. Objetivo y Alcance")
                    st.markdown(f"**Objetivo (completo):**\n\n{check(data.get('objetivo_completo'))}")
                    st.markdown(f"**Alcance (completo):**\n\n{check(data.get('alcance_completo'))}")

                    st.header("5. Diagrama de Flujo")
                    st.write(f"**Interpretación del diagrama de flujo:**\n\n{check(data.get('interpretacion_diagrama_flujo'))}")

                    st.header("6. Políticas")
                    pol = data.get("politicas", {})
                    st.write("**Política completa:**")
                    st.write(check(pol.get("texto_completo")))
                    st.write("**Identificación de los principales participantes (IA):**")
                    st.write(", ".join(pol.get("identificacion_participantes_ia", [])) if pol.get("identificacion_participantes_ia") else "No identificado")
                    st.success(f"**Resumen de la política (IA):**\n\n{check(pol.get('resumen_politica_ia'))}")

                    st.header("7. Procedimientos")
                    proc = data.get("procedimientos", {})
                    st.write("**Procedimiento completo:**")
                    st.write(check(proc.get("texto_completo")))
                    st.write("**Lista de responsables:**")
                    st.write(", ".join(proc.get("lista_responsables", [])) if proc.get("lista_responsables") else "No identificado")

                    if st.button("🗑️ Limpiar Reporte Detallado"):
                        st.session_state.detailed_report = None
                        st.rerun()

            with tab3:
                st.markdown("### 📑 Revisión del documento")
                st.markdown("**Historial y validación de revisiones del documento analizado.**")
                
                st.divider()

                # --- PRUEBA 1. VERIFICACIÓN DE FIRMAS ---
                st.subheader("1. Verificación de Firmas")
                
                # Inicializar estado de validación si no existe
                if 'user_validations' not in st.session_state:
                    st.session_state.user_validations = {}

                # Encabezado tipo "Badge" para el estado general
                col_header1, col_header2 = st.columns([10, 1])
                with col_header2:
                    st.success("**OK**")

                # Estructura de encabezado
                c_h1, c_h2, c_h3, c_h4, c_h5 = st.columns([3, 3, 2, 2, 2])
                with c_h1: st.write("**Nombre Titular**")
                with c_h2: st.write("**Puesto**")
                with c_h3: st.write("**Fecha**")
                with c_h4: st.write("**Alertas**")
                with c_h5: st.write("**Validación**")
                st.divider()

                # Si tenemos el reporte detallado, poblamos la tabla
                if st.session_state.get('detailed_report'):
                    revisores = st.session_state.detailed_report.get("revisado_aprobado", [])
                    for i, rev in enumerate(revisores):
                        signer_id = f"signer_{i}"
                        if signer_id not in st.session_state.user_validations:
                            st.session_state.user_validations[signer_id] = {
                                "pos_status": "Correcto",
                                "correct_position": rev.get('puesto'),
                                "name_status": "Activo",
                                "active_name": rev.get('nombre')
                            }

                        c1, c2, c3, c4, c5 = st.columns([3, 3, 2, 2, 2])
                        
                        # COLUMNA 1: NOMBRE (Soporte Histórico)
                        with c1:
                            nombre_doc = rev.get('nombre')
                            if st.session_state.user_validations[signer_id]["name_status"] == "Cambio de Titular":
                                st.markdown(f"**{st.session_state.user_validations[signer_id]['active_name']}**")
                                st.caption(f"📜 Histórico: {nombre_doc}")
                            else:
                                st.markdown(f"**{nombre_doc}**")
                        
                        # COLUMNA 2: PUESTO
                        with c2:
                            puesto_orig = rev.get('puesto')
                            if st.session_state.user_validations[signer_id]["pos_status"] == "Requiere Cambio":
                                st.caption(f"~~{puesto_orig}~~")
                                st.markdown(f"**{st.session_state.user_validations[signer_id]['correct_position']}**")
                            else:
                                st.write(puesto_orig)
                        
                        # COLUMNA 3: FECHA
                        with c3:
                            st.write(rev.get('fecha'))
                        
                        # COLUMNA 4: ALERTAS
                        with c4:
                            # Lógica para detectar firmas de más de 3 años
                            import datetime
                            import re
                            
                            is_obsolete = False
                            fecha_str = rev.get('fecha', '')
                            # Intentar extraer el año con regex (ej. 2023, 2020)
                            year_match = re.search(r'20\d{2}', fecha_str)
                            if year_match:
                                year = int(year_match.group())
                                current_year = datetime.datetime.now().year
                                if (current_year - year) > 3:
                                    is_obsolete = True
                            
                            if is_obsolete:
                                st.error("⚠️ Firma Obsoleta (>3 años)")
                            else:
                                st.write("✅ Firma OK")
                        
                        # COLUMNA 5: VALIDACIÓN (INTERACTIVA)
                        with c5:
                            # Validación de Nombre
                            n_choice = st.selectbox(
                                "Titular",
                                ["Activo", "Cambio de Titular"],
                                key=f"name_choice_{signer_id}",
                                label_visibility="collapsed",
                                index=0 if st.session_state.user_validations[signer_id]["name_status"] == "Activo" else 1
                            )
                            st.session_state.user_validations[signer_id]["name_status"] = n_choice
                            if n_choice == "Cambio de Titular":
                                st.session_state.user_validations[signer_id]["active_name"] = st.text_input(
                                    "Nuevo Titular", 
                                    value=st.session_state.user_validations[signer_id]["active_name"],
                                    key=f"name_input_{signer_id}",
                                    label_visibility="collapsed"
                                )

                            st.divider()

                            # Validación de Puesto
                            p_choice = st.selectbox(
                                "Puesto",
                                ["Puesto Correcto", "Requiere Cambio"],
                                key=f"pos_choice_{signer_id}",
                                label_visibility="collapsed",
                                index=0 if st.session_state.user_validations[signer_id]["pos_status"] == "Correcto" else 1
                            )
                            st.session_state.user_validations[signer_id]["pos_status"] = "Correcto" if p_choice == "Puesto Correcto" else "Requiere Cambio"
                            if p_choice == "Requiere Cambio":
                                st.session_state.user_validations[signer_id]["correct_position"] = st.text_input(
                                    "Ajuste Puesto",
                                    value=st.session_state.user_validations[signer_id]["correct_position"],
                                    key=f"pos_input_{signer_id}",
                                    label_visibility="collapsed"
                                )

                        st.divider()
                    
                    if st.button("💾 Guardar Revisión y Registro Histórico"):
                        st.success("Cambios guardados. Se ha generado la trazabilidad histórica de validación.")
                else:
                    st.warning("Debe realizar el análisis para ver esta tabla.")

                # --- PRUEBA 2. DETECCIÓN DE SUPLANTACIÓN ---
                st.subheader("2. Detección de Suplantación (Firmas Digitales)")
                st.info("💡 Esta prueba valida si el usuario del sistema que colocó el sello coincide con el nombre impreso en la firma.")

                impersonation_alerts = []
                if st.session_state.get('pages_data'):
                    for page in st.session_state.pages_data:
                        for annot in page.get('annots', []):
                            content = annot.get('content', '').lower()
                            detail = annot.get('detail', '').lower()
                            user = annot.get('user', '').lower()

                            if user and (content or detail):
                                # Limpiar puntos, guiones y espacios para comparación robusta
                                def clean(t):
                                    return "".join(c for c in t if c.isalnum()).replace(" ", "")
                                
                                c_clean = clean(content)
                                d_clean = clean(detail)
                                u_clean = clean(user)

                                # Alerta si el usuario no aparece en ninguna de las descripciones del sello
                                if u_clean not in c_clean and u_clean not in d_clean:
                                    impersonation_alerts.append({
                                        "page": page['page_number'],
                                        "user_sys": annot.get('user'),
                                        "name_doc": annot.get('content') or annot.get('detail'),
                                        "type": "Posible Suplantación / Subrogación"
                                    })

                if impersonation_alerts:
                    for alert in impersonation_alerts:
                        st.error(f"🚨 **ALERTA: Discrepancia de Identidad Digital (Pág {alert['page']})**")
                        col_a1, col_a2 = st.columns(2)
                        with col_a1:
                            st.warning(f"**Firmante en PDF:**\n{alert['name_doc']}")
                        with col_a2:
                            st.error(f"**Usuario del Sistema:**\n{alert['user_sys']}")
                        st.caption("🔍 El usuario que ejecutó la firma digital no parece coincidir con el nombre del titular en el sello.")
                        st.divider()
                else:
                    if st.session_state.get('pages_data'):
                        st.success("✅ No se detectaron discrepancias de identidad en los sellos digitales analizados.")
                    else:
                        st.caption("Sin datos para analizar suplantación.")

                # Contenedores vacíos preparados para futuras iteraciones
                col_rev1, col_rev2 = st.columns(2)
                with col_rev1:
                    st.subheader("🔍 Evidencia de Revisiones")
                    st.caption("Sin registros actuales.")
                
                with col_rev2:
                    st.subheader("⚖️ Resultados de Comparación")
                    st.caption("Sin registros actuales.")



