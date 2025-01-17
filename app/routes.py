from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form
from sqlalchemy.orm import Session
import os
from fastapi.responses import HTMLResponse
from .database import get_db
from .models import PDFModel
from .utils import create_pdf_from_images
from fastapi.responses import FileResponse

router = APIRouter()

@router.post("/imagens-para-pdf/")
async def imagens_para_pdf(
    files: list[UploadFile],
    margin_type: str = Form(...),  # Adiciona o parâmetro de margem aqui
    db: Session = Depends(get_db)
):
    # Validação do tipo de margem
    if margin_type not in ['nm', 'sm', 'mm', 'lm']:
        raise HTTPException(status_code=400, detail="Tipo de margem inválido.")

    if not files:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    # Passa o tipo de margem para a função de criação do PDF
    pdf_id, pdf_path = create_pdf_from_images(files, margin_type)

    # Registrar no banco de dados
    pdf_entry = PDFModel(id=pdf_id, file_name=f"{pdf_id}.pdf")
    db.add(pdf_entry)
    db.commit()

    return HTMLResponse(content=f"""
                        
<div><a href='/' >Voltar</a></div>
                        
<div><a href='/download/{pdf_id}' target='_blank'>{pdf_id}</a></div>
    """)

@router.get("/download/{pdf_id}")
def download_pdf(pdf_id: str, db: Session = Depends(get_db)):
    # Busca o registro do PDF no banco de dados
    pdf = db.query(PDFModel).filter(PDFModel.id == pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF não encontrado no banco de dados.")
    
    # Caminho absoluto do arquivo
    pdf_path = os.path.abspath(os.path.join("static", "output", pdf.file_name))
    print(f"PDF path: {pdf_path}")  # Log para depuração
    
    # Verifica se o arquivo existe no sistema de arquivos
    if not os.path.isfile(pdf_path):
        raise HTTPException(status_code=404, detail=f"Arquivo PDF não encontrado no servidor. Caminho: {pdf_path}")
    
    # Retorna o arquivo como resposta
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        # filename=pdf.file_name  # Nome do arquivo para download
    )

@router.get("/", response_class=HTMLResponse)
def upload_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload de Imagens para PDF</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f4f4f9;
            }
            h1 {
                color: #333;
            }
            form {
                margin-bottom: 20px;
                padding: 20px;
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            label {
                font-weight: bold;
                margin-bottom: 10px;
                display: inline-block;
            }
            input[type="file"] {
                margin: 10px 0;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #fafafa;
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                cursor: pointer;
                border-radius: 5px;
            }
            button:hover {
                background-color: #45a049;
            }
            .status {
                margin-top: 20px;
                padding: 10px;
                background-color: #e7f7e7;
                border: 1px solid #d1f5d1;
                color: #4CAF50;
            }
            .error {
                margin-top: 20px;
                padding: 10px;
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
            }
            .links {
                margin-top: 20px;
            }
            .links a {
                color: #007bff;
                text-decoration: none;
            }
            .links a:hover {
                text-decoration: underline;
            }
            #fileList {
                margin-top: 10px;
            }
            #fileList li {
                margin: 5px 0;
            }
            .radio-group {
                display: flex;
                gap: 15px;
                margin-top: 10px;
            }
            .radio-group label {
                display: flex;
                align-items: center;
                gap: 5px;
                cursor: pointer;
            }
            .radio-group input[type="radio"] {
                display: none;
            }
            .radio-group input[type="radio"] + span {
                display: inline-block;
                padding: 5px 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: #fafafa;
                transition: background-color 0.2s, border-color 0.2s;
            }
            .radio-group input[type="radio"]:checked + span {
                background-color: #4CAF50;
                color: white;
                border-color: #4CAF50;
            }
        </style>
        <script>
            function updateFileList(event) {
                const fileList = document.getElementById('fileList');
                fileList.innerHTML = '';
                const files = event.target.files;
                for (let i = 0; i < files.length; i++) {
                    let li = document.createElement('li');
                    li.textContent = files[i].name;
                    fileList.appendChild(li);
                }
            }
            function showStatus(message, isError = false) {
                const statusDiv = document.createElement('div');
                statusDiv.className = isError ? 'error' : 'status';
                statusDiv.textContent = message;
                document.body.appendChild(statusDiv);
            }
        </script>
    </head>
    <body>
        <h1>Upload de Imagens para Criar um PDF</h1>
        <form action="/imagens-para-pdf" method="POST" enctype="multipart/form-data">
            <label for="files">Selecione as imagens:</label>
            <input type="file" id="files" name="files" multiple required onchange="updateFileList(event)">
            <ul id="fileList"></ul>
            
            <label for="margin_type">Selecione o tipo de margem:</label>
            <div class="radio-group">
                <label>
                    <input type="radio" name="margin_type" value="nm" required>
                    <span>Sem Margem</span>
                </label>
                <label>
                    <input type="radio" name="margin_type" value="sm">
                    <span>Pequena</span>
                </label>
                <label>
                    <input type="radio" name="margin_type" value="mm">
                    <span>Média</span>
                </label>
                <label>
                    <input type="radio" name="margin_type" value="lm">
                    <span>Grande</span>
                </label>
            </div>
            
            <br>
            <button type="submit">Enviar</button>
        </form>

        <div class="status">
            <p>Após o upload, você poderá visualizar os PDFs gerados na página de <a href="/listar-pdfs">Listagem de PDFs</a>.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/listar-pdfs", response_class=HTMLResponse)
def listar_pdfs(db: Session = Depends(get_db)):
    pdfs = db.query(PDFModel).order_by(PDFModel.created_at.desc()).all()
    
    if not pdfs:
        html_content = "<p>Nenhum PDF encontrado.</p>"
    else:
        html_content = """
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Lista de PDFs Criados</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f4f4f9;
                }
                h1 {
                    color: #333;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                table th, table td {
                    padding: 10px;
                    border: 1px solid #ddd;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
                .links {
                    margin-top: 20px;
                }
                .links a {
                    color: #007bff;
                    text-decoration: none;
                }
                .links a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <h1>Lista de PDFs Criados</h1>
            <table>
                <thead>
                    <tr>
                        <th>Nome do Arquivo</th>
                        <th>Data de Criação</th>
                        <th>Ação</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for pdf in pdfs:
            pdf_url = f"/download/{pdf.id}"
            html_content += f"""
            <tr>
                <td>{pdf.file_name}</td>
                <td>{pdf.created_at}</td>
                <td><a href="{pdf_url}" target="_blank">Visualizar</a></td>
            </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """
    
    return HTMLResponse(content=html_content)
