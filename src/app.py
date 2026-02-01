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
from generators import pdf_report_generator
from utils import favicon_injector

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AnDo | GetAuditUP Compliance", layout="wide", page_icon="data/favicons/favicon_master.png")

# Inyectar favicons multiresolución (Si existen archivos)
try:
    if os.path.exists("src/utils/favicon_injector.py"):
        favicon_injector.inject_favicons(
            "data/favicons/favicon-16x16.png",
            "data/favicons/favicon-32x32.png",
            "data/favicons/apple-touch-icon.png"
        )
except:
    pass

# --- CUSTOM CSS: GETAUDITUP COLORS V01.01 ---
st.markdown("""
<style>
    /* 1. Títulos y Tipografía (Azul Corporativo #1F4FA3) */
    h1, h2, h3, h4, h5, h6 {
        color: #1F4FA3 !important;
    }
    
    /* 2. Botones Primarios (Verde Lima #C6E600 | Texto Azul Noche) */
    div.stButton > button[kind="primary"], .stDownloadButton > button {
        background-color: #C6E600 !important;
        color: #0F172A !important;
        border: none !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    
    /* 3. Botones Secundarios (Blanco | Texto Azul Corporativo) */
    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #1F4FA3 !important;
        border: 1px solid #1F4FA3 !important;
        border-radius: 8px !important;
    }

    /* 4. Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #C6E600 !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #64748B !important;
    }
    .stTabs [aria-selected="true"] {
        color: #1F4FA3 !important;
        font-weight: bold !important;
    }

    /* 5. Alertas de Riesgo */
    div[data-testid="stNotification-error"] {
        background-color: #FEF2F2 !important;
        color: #F87171 !important;
        border: 1px solid #F87171 !important;
    }
    div[data-testid="stNotification-warning"] {
        background-color: #F8FAFC !important;
        color: #C6E600 !important;
        border: 1px solid #C6E600 !important;
    }
    div[data-testid="stNotification-success"] {
        background-color: #F0FDF4 !important;
        color: #22C55E !important;
        border: 1px solid #22C55E !important;
    }

    /* 6. Tarjetas Interactivas (Info Card) */
    .info-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: default;
        margin-bottom: 20px;
    }
    .info-card:hover {
        transform: translateY(-5px) scale(1.01);
        box-shadow: 0 10px 15px -3px rgba(31, 79, 163, 0.2);
        border-color: #1F4FA3;
    }
    .info-card-title {
        color: #1F4FA3;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Layout head
st.title("Analizador de Documentos (AnDo)")
st.markdown("**GetAuditUP Compliance | SaaS Edition**")

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
    # Toast discreto para confirmar auth
    st.toast(f"🏢 Org: {st.session_state.organization_id}")


# Sidebar para estado y configuración
with st.sidebar:
    # --- LOGO CORPORATIVO V01.01 ---
    logo_path = "data/logo_getauditup.png"
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
        st.divider()

    st.info("Sube un PDF para comenzar el análisis.")

    # --- DESCARGA GLOBAL (V1.04) ---
    if st.session_state.get('analizado'):
        st.divider()
        st.subheader("📥 Exportar Resultados")
        global_filename = st.text_input("Nombre del archivo PDF", value=f"Reporte_AnDo_{int(time.time())}", placeholder="Reporte_AnDo_...")
        
        all_data = {
            "pages_data": st.session_state.pages_data,
            "detailed_report": st.session_state.detailed_report,
            "congruence_report": st.session_state.congruence_report,
            "index_card": st.session_state.index_card
        }
        
        pdf_bytes = pdf_report_generator.create_full_report_pdf(all_data)
        st.download_button(
            label="📄 Descargar Reporte Integral",
            data=pdf_bytes,
            file_name=f"{global_filename}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # --- FOOTER DE ESTADO (PEQUEÑO) ---
    st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True) # Empujar al final
    st.divider()
    api_key = os.getenv("GOOGLE_API_KEY")
    sb_client = get_supabase_client()
    
    status_api = "🟢 API OK" if (api_key and "PLACEHOLDER" not in api_key) else "🔴 API Mock"
    status_sb = "🟢 SB OK" if sb_client else "🟡 SB OFF"
    
    st.sidebar.caption(f"**Estado:** {status_api} | {status_sb}")
    st.sidebar.caption("© 2026 GetAuditUP. Empowered by FMConsulting.")

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
        # --- TARJETA DE INFORMACIÓN CON MOVIMIENTO ---
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">ℹ️ Información del Documento</div>
                <div style="font-size: 0.9rem; color: #64748B;">
                    <b>📂 Archivo:</b> {uploaded_file.name}<br>
                    <b>📏 Tamaño:</b> {uploaded_file.size / 1024:.2f} KB
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # 1. Registro Local (Historial de sesión)
        doc_info, is_new_local = history.register_document(temp_path)
        
        # 2. Registro SUPABASE (V1.00 - SAAS COMPLIANT)
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
                    
                    # Score de Congruencia
                    cong = idx_data.get('congruence', {})
                    score = cong.get('score', 0)
                    
                    c_idx1, c_idx2 = st.columns([1, 2])
                    with c_idx1:
                        st.metric(
                            "Score de Congruencia Semántica", 
                            f"{score}%",
                            help="Mide la alineación semántica entre lo que el documento promete en sus títulos y lo que realmente desarrolla en el texto de cada página.\n\n"
                                 "✅ 85-100%: Alineación Total\n"
                                 "⚠️ 50-84%: Alineación Parcial/Vaga\n"
                                 "❌ <50%: Incongruencia Crítica"
                        )
                    with c_idx2:
                        st.info(f"**Análisis de Congruencia:**\n{cong.get('analysis', '')}")
                    
                    # Tabla de contenidos
                    with st.expander("Ver Tabla de Contenidos Detallada", expanded=True):
                        idx_list = idx_data.get('sections', [])
                        if idx_list:
                            for item in idx_list:
                                st.write(f"🔹 **Pág {item['page']}:** {item['title']} *({item.get('observation', 'Sin observaciones')})*")
                        else:
                            st.write("No se detectaron secciones claras.")
                    
                    st.divider()


                col_t1, col_t1_dl = st.columns([3, 1])
                with col_t1:
                    st.markdown("### Interpretación de Páginas (Texto + Imágenes)")
                with col_t1_dl:
                    t1_filename = st.text_input("Nombre de pestaña 1", value="Analisis_Inicial_AnDo", label_visibility="collapsed")
                    t1_pdf = None # Placeholder por si el generador falla
                    try:
                        t1_content = {"Páginas": [f"Pág {p['page_number']}: {p.get('text_interpret', '')}" for p in pages_data]}
                        t1_pdf = pdf_report_generator.create_tab_pdf("Análisis Inicial", t1_content)
                    except: pass
                    
                    if t1_pdf:
                        st.download_button("📥 Descargar Tab 1", t1_pdf, f"{t1_filename}.pdf", "application/pdf", use_container_width=True)

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
                                
                                st.image(img['image_bytes'], caption=f"Imagen Detectada: {img['name']}", use_container_width=True)
                                if desc and desc.strip():
                                    st.warning(f"**Interpretación Técnica de Imagen:**\n\n{desc}")
                                else:
                                    st.info("No se obtuvo una interpretación detallada para esta imagen.")
                        
                        with st.status(f"Ver Texto Original Extraído (Pág {idx+1})"):
                            st.text_area("OCR/Raw Text", page['text_content'], height=150, key=f"text_{idx}")

            with tab2:
                st.markdown("### 📋 Reporte de Auditoría Detallado")
                st.caption("© 2026 GetAuditUP. Empowered by FMConsulting.")
                
                # --- DESCARGA TAB 2 ---
                t2_col1, t2_col2 = st.columns([3, 1])
                with t2_col2:
                    t2_filename = st.text_input("Nombre tab 2", value="Auditoria_Detallada_AnDo", label_visibility="collapsed")
                    if st.session_state.detailed_report:
                        t2_pdf = pdf_report_generator.create_tab_pdf("Informe de Auditoría Detallado", st.session_state.detailed_report)
                        st.download_button("📥 Descargar Tab 2", t2_pdf, f"{t2_filename}.pdf", "application/pdf", use_container_width=True)
                st.divider()

                # Mostrar reporte si ya existe (Generado automáticamente)
                if st.session_state.detailed_report:
                    data = st.session_state.detailed_report
                    st.json(data) # Mostrar simplificado para evitar errores de renderizado en copia manual

            with tab3:
                st.markdown("### 📑 Revisión del documento")
                st.markdown("**Historial y validación de revisiones del documento analizado.**")
                
                # --- DESCARGA TAB 3 ---
                t3_col1, t3_col2 = st.columns([3, 1])
                with t3_col2:
                    t3_filename = st.text_input("Nombre tab 3", value="Revision_Documento_AnDo", label_visibility="collapsed")
                    t3_content = {
                        "Congruencia": st.session_state.congruence_report.get('conclusion', {}) if st.session_state.congruence_report else "No analizado",
                        "Cruce Operativo": st.session_state.process_cross_report.get('conclusion_operativa', {}) if st.session_state.process_cross_report else "No analizado"
                    }
                    t3_pdf = pdf_report_generator.create_tab_pdf("Revisión del Documento", t3_content)
                    st.download_button("📥 Descargar Tab 3", t3_pdf, f"{t3_filename}.pdf", "application/pdf", use_container_width=True)

            with tab4:
                st.markdown("### ☁️ Gestión de Persistencia en Supabase")
                st.info("Sincroniza y versiona los resultados del análisis en la nube.")
                
                if not sb_client:
                    st.error("❌ Conexión no configurada. Agregue SUPABASE_URL y SUPABASE_KEY al archivo .env")
                elif st.session_state.detailed_report:
                    if not st.session_state.is_existing_supabase:
                        st.subheader("🆕 Documento No Registrado")
                        st.write("Presiona el botón para crear el registro inicial en la base de datos.")
                        if st.button("💾 Guardar Versión Inicial (V1) (SaaS)"):
                            doc_data = {
                                "file_name": uploaded_file.name,
                                "file_hash": file_hash,
                                "page_count": total_pages,
                                "status": "active",
                                "current_version": 1,
                                "organization_id": st.session_state.organization_id # SAAS CRITICAL FIX
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
                        # (Omitiendo lógica compleja de actualización para esta versión estable)
                        st.info("Versionado listo para activar.")

