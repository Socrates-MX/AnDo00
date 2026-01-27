from fpdf import FPDF
import io
import datetime

class AnDoPDFReport(FPDF):
    def header(self):
        # Logo placeholder (optional)
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'AnDo - Reporte de Auditoría', border=0, ln=1, align='C')
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Generado el: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', border=0, ln=1, align='R')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}} - GetAuditUP Compliance', 0, 0, 'C')

def create_tab_pdf(title, content_dict):
    """
    Creates a PDF for a specific tab's content.
    """
    pdf = AnDoPDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0, 10, title, ln=1)
    pdf.ln(5)

    pdf.set_font('helvetica', '', 11)
    for key, value in content_dict.items():
        pdf.set_font('helvetica', 'B', 12)
        pdf.multi_cell(0, 10, f"{key}:")
        pdf.set_font('helvetica', '', 11)
        if isinstance(value, list):
            for item in value:
                pdf.multi_cell(0, 8, f"- {str(item)}")
        elif isinstance(value, dict):
             for k, v in value.items():
                pdf.multi_cell(0, 8, f"  * {k}: {str(v)}")
        else:
            pdf.multi_cell(0, 8, str(value))
        pdf.ln(2)

    return pdf.output()

def create_full_report_pdf(all_data):
    """
    Creates a full PDF report with all session data.
    """
    pdf = AnDoPDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.set_font('helvetica', 'B', 20)
    pdf.cell(0, 20, 'REPORTE INTEGRAL DE AUDITORÍA', ln=1, align='C')
    pdf.ln(10)

    # 1. Dashboard / Inicial
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0, 10, '1. Análisis Inicial', ln=1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pages_data = all_data.get('pages_data', [])
    for page in pages_data:
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, f"Página {page['page_number']}", ln=1)
        pdf.set_font('helvetica', '', 10)
        pdf.multi_cell(0, 6, f"Interpretación: {page.get('text_interpret', 'N/A')}")
        pdf.ln(2)

    # 2. Análisis Detallado
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0, 10, '2. Informe de Auditoría Detallado', ln=1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    detailed = all_data.get('detailed_report', {})
    pdf.set_font('helvetica', '', 11)
    
    # Contenido Principal
    cp = detailed.get('contenido_principal', {})
    for k, v in cp.items():
        pdf.multi_cell(0, 8, f"{k.replace('_', ' ').title()}: {v}")
    
    pdf.ln(5)
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, 'Objetivo y Alcance:', ln=1)
    pdf.set_font('helvetica', '', 11)
    pdf.multi_cell(0, 8, f"Objetivo: {detailed.get('objetivo_completo')}")
    pdf.multi_cell(0, 8, f"Alcance: {detailed.get('alcance_completo')}")

    # 3. Congruencia
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0, 10, '3. Pruebas de Congruencia y Cruce', ln=1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    cong = all_data.get('congruence_report', {})
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, 'Resultado de Congruencia Estructural:', ln=1)
    pdf.set_font('helvetica', '', 11)
    pdf.multi_cell(0, 8, f"Estado: {cong.get('conclusion', {}).get('estado')}")
    pdf.multi_cell(0, 8, f"Hallazgos: {', '.join(cong.get('conclusion', {}).get('hallazgos', []))}")

    return pdf.output()
