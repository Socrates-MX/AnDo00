import pypdf

def check_annotations(file_path):
    reader = pypdf.PdfReader(file_path)
    page = reader.pages[0]
    if "/Annots" in page:
        print("--- ANNOTATIONS FOUND ---")
        for annot in page["/Annots"]:
            obj = annot.get_object()
            print(f"Type: {obj.get('/Subtype')}")
            print(f"Contents: {obj.get('/Contents')}")
            print(f"T (Title): {obj.get('/T')}")
            print(f"---")
    else:
        print("No annotations found on page 1.")

if __name__ == "__main__":
    check_annotations("data/archivo_maestro.pdf")
