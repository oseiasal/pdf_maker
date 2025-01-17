from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import uuid
from fastapi.responses import HTMLResponse

from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from fastapi import Depends

from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

# Configurar o SQLite e o SQLAlchemy
DATABASE_URL = "sqlite:///data.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo para armazenar PDFs
class PDFModel(Base):
    __tablename__ = "pdfs"
    id = Column(String, primary_key=True, index=True)
    file_name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Função para obter a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/imagens-para-pdf/")
async def imagens_para_pdf(files: list[UploadFile], db: SessionLocal = Depends(get_db)):
    if not files:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    pdf_id = str(uuid.uuid4())
    pdf_path = os.path.join(OUTPUT_DIR, f"{pdf_id}.pdf")

    imagens = []
    for file in files:
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            raise HTTPException(status_code=400, detail=f"Arquivo inválido: {file.filename}")
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
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

    # Salvar no banco de dados
    pdf_entry = PDFModel(id=pdf_id, file_name=f"{pdf_id}.pdf")
    db.add(pdf_entry)
    db.commit()

    return {"message": "PDF criado com sucesso!", "pdf_url": f"/download/{pdf_id}"}

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

@app.get("/listar-pdfs", response_class=HTMLResponse)
def listar_pdfs(db: Session = Depends(get_db)):
    pdfs = db.query(PDFModel).order_by(PDFModel.created_at.desc()).all()
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Lista de PDFs Criados</title>
    </head>
    <body>
        <h1>PDFs Criados</h1>
        <ul>
    """
    for pdf in pdfs:
        pdf_url = f"/download/{pdf.id}"
        html_content += f'<li><a href="{pdf_url}">{pdf.file_name}</a> - {pdf.created_at}</li>'
    html_content += """
        </ul>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/")
def root():
    return {"message": "Bem-vindo ao microserviço de conversão de imagens para PDF!"}
