import pypdf

def debug_pdf_text(file_path):
    reader = pypdf.PdfReader(file_path)
    page = reader.pages[0]
    text = page.extract_text()
    print("--- RAW TEXT PAGE 1 ---")
    print(repr(text))
    print("--- END ---")

if __name__ == "__main__":
    debug_pdf_text("data/archivo_maestro.pdf")
