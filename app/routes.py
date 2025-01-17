from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
import os
from fastapi.responses import HTMLResponse
from .database import get_db
from .models import PDFModel
from .utils import create_pdf_from_images
from fastapi.responses import FileResponse

router = APIRouter()

@router.post("/imagens-para-pdf/")
async def imagens_para_pdf(files: list[UploadFile], db: Session = Depends(get_db)):
    if not files:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    pdf_id, pdf_path = create_pdf_from_images(files)

    # Registrar no banco
    pdf_entry = PDFModel(id=pdf_id, file_name=f"{pdf_id}.pdf")
    db.add(pdf_entry)
    db.commit()

    return {"message": "PDF criado com sucesso!", "pdf_url": f"/download/{pdf_id}"}

@router.get("/listar-pdfs", response_class=HTMLResponse)
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

@router.get("/download/{pdf_id}")
def download_pdf(pdf_id: str, db: Session = Depends(get_db)):
    pdf = db.query(PDFModel).filter(PDFModel.id == pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF não encontrado.")
    
    pdf_path = f"static/output/{pdf.file_name}"
    return FileResponse(pdf_path, media_type="application/pdf", filename=pdf.file_name)

@router.get("/", response_class=HTMLResponse)
def upload_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload de Imagens</title>
    </head>
    <body>
        <h1>Upload de Imagens para PDF</h1>
        <form action="/imagens-para-pdf/" method="post" enctype="multipart/form-data">
            <input type="file" name="files" multiple>
            <button type="submit">Enviar</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)