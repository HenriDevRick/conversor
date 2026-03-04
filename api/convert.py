import os
import tempfile
from pdf2docx import Converter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document
import pypandoc

def handler(request):

    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": "Método não permitido"
        }

    form = request.form
    files = request.files
    conversion_type = form.get("conversion_type")

    responses = []

    for file_key in files:
        file = files[file_key]

        with tempfile.NamedTemporaryFile(delete=False) as temp_input:
            temp_input.write(file.read())
            input_path = temp_input.name

        output_path = input_path + "_converted"

        try:

            if conversion_type == "pdf_docx":
                output_path += ".docx"
                cv = Converter(input_path)
                cv.convert(output_path)
                cv.close()

            elif conversion_type == "txt_pdf":
                output_path += ".pdf"
                doc = SimpleDocTemplate(output_path)
                styles = getSampleStyleSheet()
                elements = []
                with open(input_path, "r", encoding="utf-8") as f:
                    for line in f:
                        elements.append(Paragraph(line, styles["Normal"]))
                doc.build(elements)

            elif conversion_type == "txt_docx":
                output_path += ".docx"
                document = Document()
                with open(input_path, "r", encoding="utf-8") as f:
                    for line in f:
                        document.add_paragraph(line)
                document.save(output_path)

            elif conversion_type == "odt_pdf":
                output_path += ".pdf"
                pypandoc.convert_file(input_path, 'pdf', outputfile=output_path)

            with open(output_path, "rb") as f:
                responses.append({
                    "filename": os.path.basename(output_path),
                    "content": f.read().decode("latin1")
                })

        except Exception as e:
            return {
                "statusCode": 500,
                "body": str(e)
            }

    return {
        "statusCode": 200,
        "body": str(responses)
    }