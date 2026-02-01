import streamlit as st
import os
import shutil
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar lógica del backend
from analyzers import pdf_analyzer, image_analyzer
from utils import history, diff_engine
from persistence import document_manager
from utils.supabase_client import get_supabase_client

st.set_page_config(page_title="Prototipo AnDo", layout="wide", page_icon="📄")

# Layout
# Layout Main
col_logo, col_title = st.columns([1, 5])
st.title("Analizador de Documentos (AnDo)")
st.markdown("### GetAuditUP Compliance")

# --- CONTROL DE ACCESO SAAS (Hub Integration) ---
if "organization_id" not in st.session_state:
    st.session_state.organization_id = None

# Leer parámetros de URL (Integración con Launcher)
try:
    qp = st.query_params
    org_param = qp.get("org_id", None)
    if org_param:
        st.session_state.organization_id = org_param
except:
    pass

if not st.session_state.organization_id:
    st.warning("🔒 **Modo Aislado**: Sin contexto organizacional (SaaS).")
else:
    # Toast discreto
    st.toast(f"🏢 Org: {st.session_state.organization_id}")

# Sidebar para estado y configuración
with st.sidebar:
    # Logo Principal
    if os.path.exists("data/logo_getauditup.png"):
        st.image("data/logo_getauditup.png", use_container_width=True)
    else:
        st.header("GetAuditUP")
    
    st.markdown("---")
    
    st.info("Sube un PDF para comenzar el análisis.")

    # Espaciador visual
    st.write("")
    st.write("")
    
    st.divider()
    
    # Status Indicators Minimalistas (Bottom)
    api_key = os.getenv("GOOGLE_API_KEY")
    api_ok = api_key and "PLACEHOLDER" not in api_key and api_key != "YOUR_API_KEY_HERE"
    
    sb_client = get_supabase_client()
    sb_ok = sb_client is not None

    st.caption("**Estado del Sistema:**")
    
    # Indicadores tipo "Semáforo"
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        if api_ok:
            st.markdown("🟢 API OK")
        else:
            st.markdown("🔴 API Mock")
            
    with s_col2:
        if sb_ok:
            st.markdown("🟢 SB OK")
        else:
            st.markdown("🔴 SB Error")

    st.markdown("---")
    st.caption("© 2026 GetAuditUP. Empowered by FMConsulting.")

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
        
        # 1. Registro Local (Historial de sesión)
        doc_info, is_new_local = history.register_document(temp_path)
        
        # 2. Registro SUPABASE (V1.00)
        file_hash = document_manager.calculate_pdf_hash(uploaded_file.getvalue())
        existing_doc = document_manager.check_document_existence(file_hash)
        
        if existing_doc:
            st.warning(f"🔔 Documento ya registrado en Supabase (Versión {existing_doc.get('current_version', 1)})")
            st.session_state.is_existing_supabase = True
            st.session_state.db_doc_id = existing_doc['id']
        else:
            st.info("🆕 Documento Nuevo en Supabase")
            st.session_state.is_existing_supabase = False
            st.session_state.db_doc_id = None

    # --- Estado de Sesión ---
    if 'analizado' not in st.session_state:
        st.session_state.analizado = False
    if 'pages_data' not in st.session_state:
        st.session_state.pages_data = None
    if 'congruence_report' not in st.session_state:
        st.session_state.congruence_report = None
    if 'process_cross_report' not in st.session_state:
        st.session_state.process_cross_report = None
    if 'index_card' not in st.session_state:
        st.session_state.index_card = None
    if 'is_existing_supabase' not in st.session_state:
        st.session_state.is_existing_supabase = False
    if 'db_doc_id' not in st.session_state:
        st.session_state.db_doc_id = None
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

                    # 3. ÍNDICE Y CONGRUENCIA: Generar estructura de navegación
                    from generators import report_generator
                    with st.spinner("Construyendo Índice Inteligente y validando congruencia..."):
                        st.session_state.index_card = report_generator.generate_index_card(st.session_state.pages_data)

                    # 4. PRUEBA DE CONGRUENCIA ESTRUCTURAL (IA): Validación cruzada V1.00
                    from analyzers import congruence_analyzer
                    with st.spinner("Ejecutando Prueba de Congruencia Estructural automática..."):
                        st.session_state.congruence_report = congruence_analyzer.analyze_document_congruence(
                            st.session_state.detailed_report, 
                            st.session_state.pages_data
                        )
                    
                    # 5. PRUEBA DE CRUCE OPERATIVO: Diagrama vs Procedimientos V1.00
                    from analyzers import process_cross_analyzer
                    with st.spinner("Ejecutando Cruce Diagrama vs Procedimientos..."):
                        st.session_state.process_cross_report = process_cross_analyzer.analyze_process_crossing(
                            st.session_state.detailed_report,
                            st.session_state.pages_data
                        )
                    
                    st.session_state.analizado = True
                else:
                    st.error("Error al procesar el PDF.")

        # Mostrar resultados si ya está analizado
        if st.session_state.analizado:
            pages_data = st.session_state.pages_data
            total_pages = len(pages_data)
            st.success(f"Análisis Completado: {total_pages} páginas procesadas y Reporte Detallado generado.")
            
            # Definición de Pestañas (Tabs)
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Análisis Inicial", "🔍 Análisis Detallado", "📑 Revisión del documento", "☁️ Persistencia Supabase"])

            with tab1:
                # Mostrar Índice Inteligente si existe
                if st.session_state.index_card:
                    idx_data = st.session_state.index_card
                    st.markdown(f"## 📑 {idx_data.get('title', 'Índice del Documento')}")
                    
                    cong = idx_data.get('congruence', {})
                    score = cong.get('score', 0)
                    
                    c_idx1, c_idx2 = st.columns([1, 2])
                    with c_idx1:
                        st.metric("Score de Congruencia Semántica", f"{score}%")
                    with c_idx2:
                        st.info(f"**Análisis de Congruencia:**\n{cong.get('analysis', '')}")
                    
                    with st.expander("Ver Tabla de Contenidos Detallada", expanded=True):
                        idx_list = idx_data.get('sections', [])
                        if idx_list:
                            for item in idx_list:
                                st.write(f"🔹 **Pág {item['page']}:** {item['title']} *({item.get('observation', 'Sin observaciones')})*")
                        else:
                            st.write("No se detectaron secciones claras.")
                    st.divider()

                st.markdown("### Interpretación de Páginas (Texto + Imágenes)")
                for idx, page in enumerate(pages_data):
                    with st.expander(f"Página {page['page_number']}", expanded=(idx==0)):
                        st.subheader("📝 Análisis del Contenido Escrito")
                        st.info(f"**Interpretación Ejecutiva:**\n\n{page['text_interpret']}")
                        
                        if page['images']:
                            st.subheader("🖼️ Análisis de Activos Visuales")
                            for img in page['images']:
                                desc = img['description']
                                if "[SKIP]" in desc.upper():
                                    st.caption(f"ℹ️ Imagen `{img['name']}` omitida.")
                                    continue
                                st.image(img['image_bytes'], caption=f"Imagen: {img['name']}", width=400)
                                st.warning(f"**Hallazgo en Imagen:**\n\n{desc}")
                        
                        with st.status(f"Ver Texto Original Extraído (Pág {idx+1})"):
                            st.text_area("OCR/Raw Text", page['text_content'], height=150, key=f"text_{idx}")

            with tab2:
                st.markdown("### 📋 Reporte de Auditoría Detallado")
                if st.session_state.detailed_report:
                    data = st.session_state.detailed_report
                    cp = data.get("contenido_principal", {})
                    st.write(f"**Título:** {cp.get('titulo_documento', 'N/A')}")
                    # (Simplificado para restauración rápida, la estructura completa es compleja)
                    st.json(data)
                
            with tab3:
                st.markdown("### 📑 Revisión del documento")
                st.write("Módulo de verificación de firmas y congruencia.")
                if st.session_state.congruence_report:
                    st.subheader("Congruencia Estructural")
                    st.json(st.session_state.congruence_report)
                if st.session_state.process_cross_report:
                    st.subheader("Cruce Operativo")
                    st.json(st.session_state.process_cross_report)

            with tab4:
                st.markdown("### ☁️ Gestión de Persistencia en Supabase")
                st.info("Sincroniza y versiona los resultados del análisis en la nube.")
                
                if not sb_client:
                    st.error("❌ Conexión no configurada.")
                elif st.session_state.detailed_report:
                    if not st.session_state.is_existing_supabase:
                        st.subheader("🆕 Documento No Registrado")
                        st.write("Presiona el botón para crear el registro inicial en la base de datos.")
                        if st.button("💾 Guardar Versión Inicial (V1)"):
                            doc_data = {
                                "file_name": uploaded_file.name,
                                "file_hash": file_hash,
                                "page_count": total_pages,
                                "status": "active",
                                "current_version": 1,
                                "organization_id": st.session_state.organization_id
                            }
                            if document_manager.save_new_document(doc_data, st.session_state.detailed_report):
                                st.success("✅ Documento guardado exitosamente.")
                                st.session_state.is_existing_supabase = True
                                st.rerun()
                            else:
                                st.error("Error al guardar. Verifique los logs.")
                    else:
                        st.subheader("🔄 Documento Existente")
                        st.write(f"ID del Documento: `{st.session_state.db_doc_id}`")
                        if st.button("Generar Nueva Versión"):
                             st.info("Funcionalidad de versionado lista.")
                else:
                    st.warning("Debe realizar el análisis IA antes de persistir datos.")
