import asyncio
from api.main import upload_document
from fastapi import UploadFile, File
from starlette.datastructures import Headers
import io

async def test():
    # create a mock file
    file_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Resources <<\n/Font <<\n/F1 <<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\n>>\n>>\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<< /Length 53 >>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000288 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n390\n%%EOF\n"
    uf = UploadFile(filename="test.pdf", file=io.BytesIO(file_content))
    try:
        res = await upload_document(
            file=uf,
            org_id="7a6eb435-3cdb-4e05-a463-736c2fade086",
            selected_pages="",
            extract_images="true",
            force_ocr="false",
            auth_user={"id": "e1822f9a-290f-4aba-b34c-a77931436db2", "organization_id": "7a6eb435-3cdb-4e05-a463-736c2fade086"}
        )
        print("Success:", res)
    except Exception as e:
        print("Error:", repr(e))
        import traceback
        traceback.print_exc()

asyncio.run(test())
