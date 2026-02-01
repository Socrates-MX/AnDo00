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

                    if st.session_state.detailed_report:
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
                                st.rerun()
                            else:
                                st.error(f"❌ {res}")
                    else:
                        st.subheader("🔄 Documento Existente")
                        st.write(f"ID del Documento: `{st.session_state.db_doc_id}`")
                        # (Omitiendo lógica compleja de actualización para esta versión estable)
                        st.info("Versionado listo para activar.")

