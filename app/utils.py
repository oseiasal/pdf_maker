import os
from uuid import uuid4
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image

OUTPUT_DIR = "static/output"
UPLOAD_DIR = "static/uploads"

def create_pdf_from_images(files, margin_type="nm"):
    pdf_id = str(uuid4())
    pdf_name = f"{pdf_id}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_name)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    imagens = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        imagens.append(file_path)

    c = canvas.Canvas(pdf_path, pagesize=letter)
    for imagem in imagens:
        with Image.open(imagem) as img:
            img.thumbnail((letter[0], letter[1]))
            largura, altura = img.size
            margens = {"nm": 10, "sm": 20, "mm": 30, "lm": 40}
            margem = margens.get(margin_type, 10)
            c.drawImage(imagem, x=margem, y=margem, width=largura, height=altura)
            c.showPage()

    c.save()
    for imagem in imagens:
        os.remove(imagem)

    return pdf_id, pdf_name
