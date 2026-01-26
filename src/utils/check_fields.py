import pypdf

def check_form_fields(file_path):
    reader = pypdf.PdfReader(file_path)
    fields = reader.get_fields()
    if fields:
        print("--- FORM FIELDS FOUND ---")
        for key, value in fields.items():
            print(f"{key}: {value.get('/V')}")
    else:
        print("No form fields found.")

if __name__ == "__main__":
    check_form_fields("data/archivo_maestro.pdf")
