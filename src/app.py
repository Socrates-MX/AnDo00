import streamlit as st
# Trigger reload
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
    /* --- AN-DO DESIGN SYSTEM V2.1: STRUCTURED EXECUTIVE --- */
    
    /* 1. Tipografía Global */
    h1, h2, h3, h4, h5, h6 {
        color: #1e3c72 !important; /* Royal Navy */
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* 2. BOTONES GLOBALES (Estilo Homogeneizado: IMAGEN 2 STANDARD) */
    div.stButton > button, div.stDownloadButton > button {
        /* FORMA: Rectángulo con bordes redondeados (No Pill) */
        border-radius: 8px !important; 
        
        /* TIPOGRAFÍA */
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        font-size: 15px !important;
        padding: 0.75rem 1.5rem !important;
        
        /* TRANSICIONES */
        transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }

    /* 2a. Botones PRIMARIOS y DEFAULT (Sólido Azul Ejecutivo) */
    div.stButton > button[kind="primary"], div.stButton > button:not([kind="secondary"]) {
        /* Azul Sólido Corporativo (Match Imagen 2) */
        background: #1e3c72 !important; 
        background: linear-gradient(180deg, #244280 0%, #1e3c72 100%) !important; /* Sutil degradado vertical para volumen */
        color: #ffffff !important;
    }
    div.stButton > button[kind="primary"]:hover, div.stButton > button:not([kind="secondary"]):hover {
        background: #2a5298 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(30, 60, 114, 0.2) !important;
    }
    div.stButton > button[kind="primary"]:active, div.stButton > button:not([kind="secondary"]):active {
        background: #162c55 !important;
        transform: translateY(1px);
    }

    /* 2b. Botones SECUNDARIOS (Outline / Ghost) */
    div.stButton > button[kind="secondary"] {
        background-color: transparent !important;
        border: 2px solid #1e3c72 !important;
        color: #1e3c72 !important;
        box-shadow: none !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #f0f4f8 !important;
        color: #2a5298 !important;
        border-color: #2a5298 !important;
    }

    /* 2c. Botones de Descarga (Distintivo pero congruente) */
    div.stDownloadButton > button {
        background: #008f39 !important; /* Excel Green Standard */
        color: white !important;
    }
    div.stDownloadButton > button:hover {
         background: #00a642 !important;
    }

    /* 2d. Fix TEXTO interno */
    div.stButton > button p, div.stDownloadButton > button p {
        font-weight: 700 !important;
        font-size: 15px !important;
    }

    /* 3. Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #1e3c72 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #1e3c72 !important;
        font-weight: bold !important;
    }
    .stTabs [aria-selected="false"] {
        color: #64748B !important;
    }

    /* 4. Tarjetas Informativas */
    .info-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px; /* Matching buttons */
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .info-card-title {
        color: #1e3c72;
        font-weight: 800;
        font-size: 1.1rem;
        margin-bottom: 10px;
    }

    /* 5. WHITELABEL / MODO PROPIETARIO (Ocultar UI Streamlit) */
    
    /* Ocultar Botón 'Deploy' (Selectores Agresivos para múltiples versiones) */
    .stDeployButton, 
    [data-testid="stDeployButton"],
    [data-testid="stAppDeployButton"], 
    button[kind="header"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    
    /* Ocultar específicamente el contenedor del botón deploy si está anidado */
    header > div:first-of-type > div > div > div {
        display: none !important; 
    }
    
    /* Asegurar que el menú de 3 puntos (Settings) siga visible */
    /* El menú suele estar en un contenedor hermano al deploy. 
       Al ocultar el stDeployButton debería bastar. 
       Si se borró todo el header, restauramos el menú específicamente: */
    
    #MainMenu {
        visibility: visible !important;
        display: block !important;
    }

    /* Ocultar Footer 'Made with Streamlit' */
    footer {
        visibility: hidden !important;
        height: 0px !important;
    }
    
    /* Ocultar Icono de Estado (Corredor) */
    div[data-testid="stStatusWidget"] {
        display: none !important;
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
            st.session_state.db_doc_version = existing_doc.get('current_version', 1)
            
            # Recuperar contenido de la última versión para comparación
            latest = document_manager.get_latest_analysis(existing_doc['id'])
            if latest:
                st.session_state.cloud_latest_payload = latest.get('full_analysis_payload')
        else:
            st.info("🆕 Documento Nuevo en Supabase")
            st.session_state.is_existing_supabase = False
            st.session_state.db_doc_id = None
            st.session_state.cloud_latest_payload = None

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
    if 'cloud_latest_payload' not in st.session_state:
        st.session_state.cloud_latest_payload = None

    with col2:
        st.subheader("Resultados del Análisis")
        
        if st.button("INICIAR PROCESAMIENTO PARA EL ANÁLISIS"):
            # Usar st.status para un log de ejecución profesional y unificado
            with st.status("Iniciando procesamiento de análisis del documento...", expanded=True) as status:
                
                # FASE 1: EXTRACCIÓN
                st.write("**Fase 1/5:** Digitalizando documento y extrayendo texto (OCR)...")
                st.session_state.pages_data, st.session_state.pdf_meta = pdf_analyzer.analyze_pdf(temp_path)
                
                if st.session_state.pages_data:
                    # Interpretación de páginas e imágenes
                    st.write("**Fase 2/5:** Analizando elementos visuales e imágenes...")
                    progress_bar = st.progress(0)
                    total_p = len(st.session_state.pages_data)
                    
                    for i, page in enumerate(st.session_state.pages_data):
                        page['text_interpret'] = image_analyzer.generate_text_interpretation(page['text_content'])
                        time.sleep(0.1) 
                        for img in page.get('images', []):
                            img['description'] = image_analyzer.generate_image_description(img['image_bytes'])
                            time.sleep(0.1)
                        progress_bar.progress((i + 1) / total_p)
                    progress_bar.empty()
                    
                    # FASE 3: ESTRUCTURACIÓN (Informe Detallado)
                    st.write("**Fase 3/5:** Generando Informe Estructural del Análisis (Deep Analysis)...")
                    from analyzers import detailed_analyzer
                    
                    detailed_json_raw = detailed_analyzer.extract_detailed_analysis(st.session_state.pages_data, temp_path)
                    try:
                        import json
                        st.session_state.detailed_report = json.loads(detailed_json_raw)
                    except Exception as e:
                        st.error(f"Error crítico en Fase 3: {e}")
                        status.update(label="Error de Proceso", state="error")

                    if st.session_state.detailed_report:
                        # FASE 4: ÍNDICE Y CONGRUENCIA
                        st.write("**Fase 4/5:** Construyendo Índice Lógico y Validando Congruencia...")
                        from generators import report_generator
                        st.session_state.index_card = report_generator.generate_index_card(st.session_state.pages_data)

                        # Validación cruzada
                        from analyzers import congruence_analyzer
                        st.session_state.congruence_report = congruence_analyzer.analyze_document_congruence(
                            st.session_state.detailed_report, 
                            st.session_state.pages_data
                        )
                        
                        # FASE 5: CRUCE OPERATIVO
                        st.write("**Fase 5/5:** Ejecutando Cruce Diagrama vs Procedimientos...")
                        from analyzers import process_cross_analyzer
                        st.session_state.process_cross_report = process_cross_analyzer.analyze_process_crossing(
                            st.session_state.detailed_report,
                            st.session_state.pages_data
                        )
                        
                        status.update(label="Procesamiento de Análisis Completo Exitosamente", state="complete", expanded=False)

                    else:
                        st.warning("⚠️ El Reporte Detallado no se pudo generar (posible error de API Key). Se omiten las pruebas de congruencia y cruce.")

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
                    if ra_data: 
                        st.table(ra_data)
                    else: 
                        st.info("No identificado en el documento")

                    st.header("4. Objetivo y Alcance")
                    st.markdown(f"**Objetivo (completo):**\n\n{check(data.get('objetivo_completo'))}")
                    st.markdown(f"**Alcance (completo):**\n\n{check(data.get('alcance_completo'))}")

                    st.header("5. Diagrama de Flujo")
                    st.write(f"**Interpretación del diagrama de flujo:**\n\n{check(data.get('interpretacion_diagrama_flujo'))}")

                    st.header("6. Políticas")
                    pol = data.get("politicas", {})
                    st.write("**Política completa:**")
                    with st.expander("Ver Texto Completo de Políticas"):
                        st.write(check(pol.get("texto_completo")))
                    st.write("**Identificación de los principales participantes (IA):**")
                    st.write(", ".join(pol.get("identificacion_participantes_ia", [])) if pol.get("identificacion_participantes_ia") else "No identificado")
                    st.success(f"**Resumen de la política (IA):**\n\n{check(pol.get('resumen_politica_ia'))}")

                    st.header("7. Procedimientos")
                    proc = data.get("procedimientos", {})
                    st.write("**Procedimiento completo:**")
                    with st.expander("Ver Texto Completo de Procedimientos"):
                         st.write(check(proc.get("texto_completo")))
                    st.write("**Lista de responsables:**")
                    st.write(", ".join(proc.get("lista_responsables", [])) if proc.get("lista_responsables") else "No identificado")

                    if st.button("🗑️ Limpiar Reporte Detallado"):
                        st.session_state.detailed_report = None
                        st.session_state.analizado = False
                        st.rerun()

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
                    if not revisores:
                        st.info("No se identificaron firmantes en la sección de 'Revisado y Aprobado'.")
                    
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

                                # EVITAR FALSOS POSITIVOS: Si el contenido es solo fecha/números, ignorar alerta de nombre
                                is_date_only = len(c_clean) < 15 and c_clean.isdigit() # Simple heuristica para fechas limpias 
                                
                                if not is_date_only:
                                    # Alerta si el usuario no aparece en ninguna de las descripciones del sello
                                    if u_clean not in c_clean and u_clean not in d_clean:
                                        impersonation_alerts.append({
                                            "page": f"{page['page_number']} (Metadatos)",
                                            "user_sys": annot.get('user'),
                                            "name_doc": annot.get('content') or annot.get('detail'),
                                            "type": "Posible Suplantación (Metadatos PDF)"
                                        })

                # 2. VALIDACIÓN VISUAL CRUZADA (Tabla de Firmas vs Texto de Firma)
                if st.session_state.get('detailed_report'):
                    st.info("""
                    ℹ️ **¿Qué busca esta prueba?**
                    Esta herramienta verifica la **coherencia de identidad** comparando dos fuentes:
                    1. El **Nombre del Titular** listado en la columna 'Nombre' del documento PDF.
                    2. La **Identidad Digital** extraída del texto del sello/firma electrónica (ej. 'Firmado por...').
                    
                    *Detecta casos donde el titular del puesto no coincide con la persona que realmente ejecutó la firma digital.*
                    """)
                    
                    revisores = st.session_state.detailed_report.get('revisado_aprobado', [])
                    
                    # Función de normalización avanzada (Tokens)
                    import unicodedata
                    def get_tokens(text):
                        # 1. Quitar acentos: Sánchez -> Sanchez
                        text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
                        # 2. Minusculas y alfanumérico
                        text = "".join(c if c.isalnum() else " " for c in text.lower())
                        # 3. Set de palabras (tokens)
                        return set(text.split())

                    for rev in revisores:
                        firma_txt = rev.get('firma', '')
                        nombre_titular = rev.get('nombre', '')
                        
                        if "Firmado Electrónicamente por:" in firma_txt:
                            # Extraer nombre del sello
                            nombre_sello = firma_txt.replace("Firmado Electrónicamente por:", "").strip()
                            
                            tokens_titular = get_tokens(nombre_titular)
                            tokens_sello = get_tokens(nombre_sello)
                            
                            # Criterio: ¿Las palabras del titular están contenidas en el sello? (o viceversa)
                            # Ejemplo: {iliana, sanchez} ⊂ {iliana, denise, sanchez, estudillo} -> TRUE
                            match = tokens_titular.issubset(tokens_sello) or tokens_sello.issubset(tokens_titular)
                            
                            # Si no coinciden, es alerta
                            if not match:
                                impersonation_alerts.append({
                                    "page": "Tabla de Firmas",
                                    "user_sys": nombre_sello, 
                                    "name_doc": nombre_titular, 
                                    "type": "Discrepancia Visual de Identidad"
                                })

                if st.session_state.get('pdf_meta'):
                    meta = st.session_state.pdf_meta
                    with st.expander("📂 Ficha Técnica del Documento (Metadatos & Seguridad)", expanded=False):
                        import datetime
                        
                        # --- HELPERS ---
                        def parse_pdf_date(date_str):
                            if not date_str: return "Desconocido"
                            # Clean "D:" prefix and timezone like "-07'00'"
                            clean = date_str.replace("D:", "").split('+')[0].split('-')[0].replace("'","")
                            try:
                                # Format: YYYYMMDDHHMMSS
                                dt = datetime.datetime.strptime(clean[:14], "%Y%m%d%H%M%S")
                                return dt.strftime("%d/%b/%Y %H:%M Hrs")
                            except:
                                return date_str

                        # --- EXTRACTION ---
                        creator_tool = meta.get('Creator', 'Desconocido')
                        producer = meta.get('Producer', 'Desconocido')
                        author = meta.get('Author', 'No especificado')
                        creation_date = parse_pdf_date(meta.get('CreationDate'))
                        mod_date = parse_pdf_date(meta.get('ModDate'))
                        is_encrypted = meta.get('is_encrypted', False)

                        # --- ANALYSIS ---
                        origin_type = "Software PDF Genérico"
                        if "Word" in creator_tool or "Excel" in creator_tool: origin_type = "Microsoft Office (Nativo)"
                        elif "Scanner" in creator_tool or "image" in producer.lower(): origin_type = "Escaneado / Imagen"
                        elif "Canva" in creator_tool: origin_type = "Diseño (Canva)"
                        
                        # --- DISPLAY (Custom CSS Cards) ---
                        st.markdown("""
                        <style>
                        .meta-card {
                            background-color: rgba(128, 128, 128, 0.05);
                            border-radius: 8px;
                            padding: 15px;
                            border: 1px solid rgba(128, 128, 128, 0.15);
                            height: 100%;
                        }
                        .meta-label {
                            font-size: 0.8em;
                            opacity: 0.7;
                            text-transform: uppercase;
                            margin-bottom: 4px;
                            font-weight: 600;
                        }
                        .meta-main {
                            font-size: 1.1em;
                            font-weight: 500;
                            margin-bottom: 8px;
                        }
                        .meta-sub {
                            font-size: 0.75em;
                            opacity: 0.6;
                            line-height: 1.2;
                            overflow-wrap: break-word;
                        }
                        </style>
                        """, unsafe_allow_html=True)

                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"""
                            <div class="meta-card">
                                <div class="meta-label">🖥️ Origen Digital</div>
                                <div class="meta-main">{origin_type}</div>
                                <div class="meta-sub">{creator_tool}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class="meta-card">
                                <div class="meta-label">👤 Autor Registrado</div>
                                <div class="meta-main">{author}</div>
                                <div class="meta-sub">{producer}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        with col3:
                            sec_icon = "🔒" if is_encrypted else "🔓"
                            sec_txt = "Encriptado" if is_encrypted else "Abierto / Estándar"
                            st.markdown(f"""
                            <div class="meta-card">
                                <div class="meta-label">🛡️ Nivel de Seguridad</div>
                                <div class="meta-main">{sec_icon} {sec_txt}</div>
                                <div class="meta-sub">Permisos: Lectura/Escritura/Impresión (Estándar)</div>
                            </div>
                            """, unsafe_allow_html=True)

                        st.write("") # Spacer

                        # Timeline Section
                        st.markdown("##### ⏳ Línea de Tiempo del Documento")
                        tl1, tl2 = st.columns(2)
                        with tl1:
                             st.info(f"**📅 Fecha de Creación:**\n\n{creation_date}")
                        with tl2:
                             mod_color = "blue" if creation_date == mod_date else "orange"
                             # Usando sintaxis de color de Streamlit en markdown
                             st.markdown(f"""
                             <div style="padding:10px; border-radius:5px; background-color: rgba(255, 165, 0, 0.1) if '{mod_color}'=='orange' else rgba(0,0,255,0.05); border-left: 5px solid {mod_color};">
                                <strong>📝 Última Modificación:</strong><br>{mod_date}
                             </div>
                             """, unsafe_allow_html=True)

                        if creation_date != mod_date and creation_date != "Desconocido" and mod_date != "Desconocido":
                            st.caption("ℹ️ *Nota: La diferencia entre fechas indica que el documento fue editado y guardado nuevamente después de su generación inicial.*")

                if impersonation_alerts:
                    for alert in impersonation_alerts:
                        # Diferenciar Severidad: Metadatos (Warning) vs Visual (Error Crítico)
                        is_metadata_warning = "Metadatos" in alert['type']
                        
                        if is_metadata_warning:
                            st.warning(f"⚠️ **ADVERTENCIA DE CONTEXTO: {alert['type']}**")
                            explanation = "El usuario técnico que generó/consolidó el PDF no coincide con la firma. Esto es común si un administrador generó el documento final."
                        else:
                            st.error(f"🚨 **ALERTA CRÍTICA: {alert['type']}**")
                            explanation = "El nombre visual en la firma NO coincide con el nombre del titular esperado."

                        col_a1, col_a2 = st.columns(2)
                        with col_a1:
                            st.caption("Firmante en PDF:")
                            st.write(f"**{alert['name_doc']}**")
                        with col_a2:
                            st.caption("Usuario del Sistema / Sello:")
                            st.write(f"**{alert['user_sys']}**")
                        
                        st.caption(f"🔍 {explanation}")
                        st.divider()
                else:
                    if st.session_state.get('pages_data'):
                        st.success("✅ No se detectaron discrepancias de identidad en los sellos digitales analizados.")
                    else:
                        st.caption("Sin datos para analizar suplantación.")

                # --- PRUEBA 3. CONGRUENCIA ESTRUCTURAL (IA) ---
                st.divider()
                st.subheader("3. Prueba de Congruencia Estructural (IA)")
                st.info("🎯 Esta prueba utiliza IA para validar la alineación lógica entre Título, Objetivo, Alcance, Políticas y Procedimientos.")

                if st.session_state.get('detailed_report'):
                    if st.session_state.get('congruence_report'):
                        cr = st.session_state.congruence_report
                        
                        # Conclusión General
                        estado = cr.get("conclusion", {}).get("estado", "No disponible")
                        if "✅" in estado or "Congruente" in estado and "No" not in estado:
                            st.success(f"### Resultado Final: {estado}")
                        elif "⚠️" in estado or "Parcialmente" in estado:
                            st.warning(f"### Resultado Final: {estado}")
                        else:
                            st.error(f"### Resultado Final: {estado}")

                        # Matriz de Congruencia
                        st.markdown("#### Matriz de Congruencia")
                        import pandas as pd
                        df = pd.DataFrame(cr.get("matriz", []))
                        st.table(df)

                        # Hallazgos y Riesgos EDITABLES
                        st.markdown("---")
                        c_res1, c_res2 = st.columns(2)
                        
                        # Obtener listas actuales del estado de sesión
                        hallazgos = cr.get("conclusion", {}).get("hallazgos", [])
                        riesgos = cr.get("conclusion", {}).get("riesgos", [])

                        with c_res1:
                            st.markdown("**🔍 Hallazgos Clave**")
                            # Hack para mostrar lista si no hay botón de editar, simplificado para restore
                            for h in hallazgos:
                                st.write(f"- {h}")

                        with c_res2:
                            st.markdown("**🚨 Riesgos Detectados**")
                            for r in riesgos:
                                st.write(f"- {r}")
                        
                        st.info(f"**Impacto en Auditoría (Opcional):** {cr.get('conclusion', {}).get('impacto', 'N/A')}")
                else:
                    st.warning("Debe realizar el análisis detallado previamente para habilitar esta prueba.")

                # --- PRUEBA 4. CRUCE OPERATIVO (DIAGRAMA vs PROCEDIMIENTOS) ---
                st.divider()
                st.subheader("4. Prueba de Cruce Operativo (Diagrama vs Procedimientos)")
                st.info("🔄 Esta prueba valida la correspondencia paso a paso entre el Diagrama de Flujo y los Procedimientos escritos.")

                if st.session_state.get('process_cross_report'):
                    px = st.session_state.process_cross_report
                    
                    # Conclusión Operativa
                    estado_px = px.get("conclusion_operativa", {}).get("estado", "No disponible")
                    if "✅" in estado_px or "Congruente" in estado_px and "No" not in estado_px:
                        st.success(f"### Resultado Final: {estado_px}")
                    elif "⚠️" in estado_px or "Parcialmente" in estado_px:
                        st.warning(f"### Resultado Final: {estado_px}")
                    else:
                        st.error(f"### Resultado Final: {estado_px}")

                    # Matriz de Cruce
                    st.markdown("#### Matriz de Cruce")
                    import pandas as pd
                    df_px = pd.DataFrame(px.get("matriz", []))
                    st.table(df_px)
                    
                    st.info(f"**Impacto Operativo:** {px.get('conclusion_operativa', {}).get('impacto', 'N/A')}")
                else:
                    st.caption("Esperando resultados del cruce operativo...")

            with tab4:
                st.markdown("### ☁️ Gestión de Persistencia en Supabase")
                st.info("Sincroniza y versiona los resultados del análisis en la nube.")
                
                if not sb_client:
                    st.error("❌ Conexión no configurada. Agregue SUPABASE_URL y SUPABASE_KEY al archivo .env")
                elif st.session_state.detailed_report:
                    if not st.session_state.is_existing_supabase:
                        st.subheader("🆕 Documento No Registrado")
                        st.write("Presiona el botón para crear el registro inicial en la base de datos.")
                        
                        # Fallback para Desarrollo Local: Si no hay Org ID, usar el ID del script ENSURE_DEMO_ORG.sql
                        target_org_id = st.session_state.organization_id
                        if not target_org_id:
                            target_org_id = "00000000-0000-0000-0000-000000000000"
                            st.caption("⚠️ Modo Demo Local Activado (ID: 0000...0000)")

                        if st.button("💾 Guardar Versión Inicial (V1) (SaaS)"):
                            doc_data = {
                                "file_name": uploaded_file.name,
                                "file_hash": file_hash,
                                "page_count": total_pages,
                                "status": "active",
                                "current_version": 1,
                                "organization_id": target_org_id 
                            }
                            
                            res = document_manager.save_new_document(doc_data, st.session_state.detailed_report)
                            
                            if res is True:
                                st.success("✅ Documento guardado exitosamente.")
                                st.session_state.is_existing_supabase = True
                                st.session_state.db_doc_version = 1
                                st.rerun()
                            else:
                                st.error(f"❌ {res}")
                    else:
                        st.subheader("🔄 Documento Existente")
                        st.write(f"ID del Documento: `{st.session_state.db_doc_id}`")
                        
                        curr_v = st.session_state.get('db_doc_version', 1)
                        next_v = curr_v + 1
                        
                        st.markdown(f"Edición Actual en Nube: **V{curr_v}**")

                        # --- DETECCIÓN DE CAMBIOS (HASHING) ---
                        import hashlib
                        import json
                        
                        has_changes = True # Por defecto asumimos cambios por seguridad
                        
                        if st.session_state.get('cloud_latest_payload'):
                            try:
                                def get_hash(obj):
                                    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()
                                
                                local_hash = get_hash(st.session_state.detailed_report)
                                cloud_hash = get_hash(st.session_state.cloud_latest_payload)
                                
                                if local_hash == cloud_hash:
                                    has_changes = False
                            except Exception as e:
                                print(f"Error hashing: {e}")
                        
                        allow_save = False
                        
                        if not has_changes:
                            st.success("✅ **Sincronizado:** El análisis actual es idéntico a la versión en la nube.")
                            if st.checkbox("Forzar creación de nueva versión de todos modos"):
                                allow_save = True
                        else:
                            st.warning("⚠️ **Cambios Detectados:** El análisis local difiere de la última versión guardada.")
                            allow_save = True
                        
                        if allow_save:
                            if st.button(f"✨ Guardar Nueva Versión (V{next_v})", type="primary"):
                                res = document_manager.update_document_version(
                                    st.session_state.db_doc_id,
                                    next_v,
                                    st.session_state.detailed_report
                                )
                                if res is True:
                                    st.success(f"✅ Versión {next_v} actualizada correctamente.")
                                    st.session_state.db_doc_version = next_v
                                    # Actualizar referencia cloud para futuros checks sin recarga
                                    st.session_state.cloud_latest_payload = st.session_state.detailed_report
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"❌ {res}")

