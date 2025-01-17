from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import uuid
from fastapi.responses import HTMLResponse

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/imagens-para-pdf/")
async def imagens_para_pdf(files: list[UploadFile]):
    if not files:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    # Gerar um ID único para o PDF
    pdf_id = str(uuid.uuid4())
    pdf_path = os.path.join(OUTPUT_DIR, f"{pdf_id}.pdf")

    # Salvar imagens no diretório temporário
    imagens = []
    for file in files:
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            raise HTTPException(status_code=400, detail=f"Arquivo inválido: {file.filename}")
        
        # Salvar arquivo localmente
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        imagens.append(file_path)

    # Criar o PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    for imagem in imagens:
        with Image.open(imagem) as img:
            # Redimensionar a imagem para caber na página
            img.thumbnail((letter[0], letter[1]))
            largura, altura = img.size
            c.drawImage(imagem, x=(letter[0] - largura) / 2, y=(letter[1] - altura) / 2, width=largura, height=altura)
            c.showPage()

    c.save()

    # Limpar arquivos temporários
    for imagem in imagens:
        os.remove(imagem)

    return {"message": "PDF criado com sucesso!", "pdf_url": f"http://localhost:8000/download/{pdf_id}"}

@app.get("/download/{pdf_id}")
async def download_pdf(pdf_id: str):
    pdf_path = os.path.join(OUTPUT_DIR, f"{pdf_id}.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF não encontrado.")
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"{pdf_id}.pdf")

@app.get("/upload", response_class=HTMLResponse)
def upload_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload de Imagens para PDF</title>
    </head>
    <body>
        <h1>Upload de Imagens para PDF</h1>
        <form id="uploadForm" method="post" action="/imagens-para-pdf/" enctype="multipart/form-data">
            <label for="files">Selecione as imagens:</label>
            <input type="file" id="files" name="files" multiple accept="image/*">
            <br><br>
            <button type="submit">Enviar</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/")
def root():
    return {"message": "Bem-vindo ao microserviço de conversão de imagens para PDF!"}
