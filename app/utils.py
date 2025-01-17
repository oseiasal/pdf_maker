import os
from uuid import uuid4
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

UPLOAD_DIR = "static/uploads"
OUTPUT_DIR = "static/output"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_pdf_from_images(files):
    pdf_id = str(uuid4())
    pdf_path = os.path.join(OUTPUT_DIR, f"{pdf_id}.pdf")

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
            c.drawImage(imagem, x=(letter[0] - largura) / 2, y=(letter[1] - altura) / 2, width=largura, height=altura)
            c.showPage()

    c.save()
    for imagem in imagens:
        os.remove(imagem)

    return pdf_id, pdf_path
