from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
from fastapi.responses import HTMLResponse, FileResponse
from rembg import remove
from concurrent.futures import ThreadPoolExecutor
import os


executor = ThreadPoolExecutor(max_workers=8)
bg_router = APIRouter()

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@bg_router.get("/remove_bg", response_class=HTMLResponse)
async def homepage():
    """Exibe a página HTML para upload de arquivos."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Remover Fundo de Imagens</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .preview { max-width: 300px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>Remover Fundo de Imagens</h1>
        <form id="uploadForm">
            <label for="file">Escolha uma imagem (PNG, JPG ou JPEG):</label>
            <input type="file" id="file" name="file" accept="image/png, image/jpeg, image/jpg" required>
            <div>
                <h3>Pré-visualização:</h3>
                <img id="preview" class="preview" src="" alt="Nenhuma imagem selecionada">
            </div>
            <button type="submit">Enviar</button>
        </form>
        <div id="result" style="display:none;">
            <h3>Resultado:</h3>
            <img id="output" class="preview" src="" alt="Imagem processada">
        </div>
        <script>
            // Exibir pré-visualização da imagem selecionada
            const fileInput = document.getElementById('file');
            const preview = document.getElementById('preview');
            const uploadForm = document.getElementById('uploadForm');
            const resultDiv = document.getElementById('result');
            const outputImage = document.getElementById('output');

            fileInput.addEventListener('change', () => {
                const file = fileInput.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        preview.src = e.target.result;
                    };
                    reader.readAsDataURL(file);
                }
            });

            // Enviar o arquivo e exibir o resultado
            uploadForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                const response = await fetch('/remove-bg/', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const data = await response.json();
                    outputImage.src = data.output_url;
                    resultDiv.style.display = 'block';
                } else {
                    alert('Erro ao processar a imagem.');
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

def process_image(input_data: bytes, output_path: str):
    """Remove o fundo da imagem e salva o resultado no caminho especificado."""
    output_data = remove(input_data)
    with open(output_path, "wb") as output_file:
        output_file.write(output_data)

@bg_router.post("/remove-bg/")
async def remove_background(file: UploadFile = File(...)):
    """Processa o arquivo enviado e remove o fundo da imagem."""
    if not file.filename.lower().endswith(("png", "jpg", "jpeg")):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem (PNG, JPG ou JPEG).")
    
    try:
        # Lê o arquivo enviado
        input_data = await file.read()

        # Salva o arquivo original
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(input_path, "wb") as input_file:
            input_file.write(input_data)

        # Define o caminho do arquivo de saída
        output_path = os.path.join(OUTPUT_FOLDER, f"output_{file.filename}")

        # Envia a tarefa para o executor de threads
        future = executor.submit(process_image, input_data, output_path)

        # Aguarda a conclusão do processamento
        future.result()  # Espera a execução da tarefa

        # Remove os arquivos após o processamento
        os.remove(input_path)
        # os.remove(output_path)

        # Retorna a URL do arquivo processado
        return {"output_url": f"/output/output_{file.filename}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar a imagem: {str(e)}")