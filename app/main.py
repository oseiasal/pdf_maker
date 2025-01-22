from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
import os


from app.routes import router
from app.database import Base, engine
from app.utils import criar_pastas_necessarias




# Inicializa o banco de dados
Base.metadata.create_all(bind=engine)

# cria as pastas se necessário

criar_pastas_necessarias()

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="sua_chave_secreta")
# Montando pastas de saída para servir arquivos
app.mount("/output", StaticFiles(directory="output"), name="output")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Inclui as rotas
app.include_router(router)
