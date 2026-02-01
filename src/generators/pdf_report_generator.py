from fpdf import FPDF
import io
import datetime

import os

class AnDoPDFReport(FPDF):
    def header(self):
        # --- LOGO CORPORATIVO V01.01 ---
        logo_path = "data/logo_getauditup.png"
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 45) # Posición X, Y y Ancho
            self.ln(12)
        
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'AnDo - Reporte de Auditoría', border=0, ln=1, align='C')
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Generado el: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', border=0, ln=1, align='R')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}} - GetAuditUP Compliance', 0, 0, 'C')

def safe_text(text):
    """Limpia el texto de caracteres que pueden romper FPDF o no están en latin-1"""
    if not text: return ""
    return str(text).encode('latin-1', 'ignore').decode('latin-1')

def create_tab_pdf(title, content_dict):
    """
    Creates a PDF for a specific tab's content.
    """
    pdf = AnDoPDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 16)
    pdf.multi_cell(0, 10, safe_text(title), new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)

    for key, value in content_dict.items():
        pdf.set_font('helvetica', 'B', 12)
        pdf.multi_cell(0, 10, f"{safe_text(key)}:", new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('helvetica', '', 11)
        if isinstance(value, list):
            for item in value:
                pdf.multi_cell(0, 8, f"- {safe_text(item)}", new_x='LMARGIN', new_y='NEXT')
        elif isinstance(value, dict):
             for k, v in value.items():
                pdf.multi_cell(0, 8, f"  * {safe_text(k)}: {safe_text(v)}", new_x='LMARGIN', new_y='NEXT')
        else:
            pdf.multi_cell(0, 8, safe_text(value), new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)

    return bytes(pdf.output())

def create_full_report_pdf(all_data):
    """
    Creates a full PDF report with all session data.
    """
    pdf = AnDoPDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.set_font('helvetica', 'B', 20)
    pdf.multi_cell(0, 20, 'REPORTE INTEGRAL DE AUDITORÍA', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(10)

    # 1. Dashboard / Inicial
    pdf.set_font('helvetica', 'B', 16)
    pdf.multi_cell(0, 10, '1. Análisis Inicial', new_x='LMARGIN', new_y='NEXT')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pages_data = all_data.get('pages_data', [])
    for page in pages_data:
        pdf.set_font('helvetica', 'B', 12)
        pdf.multi_cell(0, 10, f"Página {page['page_number']}", new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('helvetica', '', 10)
        pdf.multi_cell(0, 6, f"Interpretación: {safe_text(page.get('text_interpret', 'N/A'))}", new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)

    # 2. Análisis Detallado
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 16)
    pdf.multi_cell(0, 10, '2. Informe de Auditoría Detallado', new_x='LMARGIN', new_y='NEXT')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    detailed = all_data.get('detailed_report', {})
    pdf.set_font('helvetica', '', 11)
    
    # Contenido Principal
    cp = detailed.get('contenido_principal', {})
    for k, v in cp.items():
        pdf.multi_cell(0, 8, f"{safe_text(k.replace('_', ' ').title())}: {safe_text(v)}", new_x='LMARGIN', new_y='NEXT')
    
    pdf.ln(5)
    pdf.set_font('helvetica', 'B', 12)
    pdf.multi_cell(0, 10, 'Objetivo y Alcance:', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('helvetica', '', 11)
    pdf.multi_cell(0, 8, f"Objetivo: {safe_text(detailed.get('objetivo_completo'))}", new_x='LMARGIN', new_y='NEXT')
    pdf.multi_cell(0, 8, f"Alcance: {safe_text(detailed.get('alcance_completo'))}", new_x='LMARGIN', new_y='NEXT')

    # 3. Congruencia
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 16)
    pdf.multi_cell(0, 10, '3. Pruebas de Congruencia y Cruce', new_x='LMARGIN', new_y='NEXT')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    cong = all_data.get('congruence_report', {})
    pdf.set_font('helvetica', 'B', 12)
    pdf.multi_cell(0, 10, 'Resultado de Congruencia Estructural:', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('helvetica', '', 11)
    if cong:
        pdf.multi_cell(0, 8, f"Estado: {safe_text(cong.get('conclusion', {}).get('estado'))}", new_x='LMARGIN', new_y='NEXT')
        hallazgos = cong.get('conclusion', {}).get('hallazgos', [])
        pdf.multi_cell(0, 8, f"Hallazgos: {safe_text(', '.join(hallazgos))}", new_x='LMARGIN', new_y='NEXT')

    return bytes(pdf.output())
