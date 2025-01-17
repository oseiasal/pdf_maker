from fastapi import FastAPI
from app.routes import router
from app.database import Base, engine
from app.utils import criar_pastas_necessarias

# Inicializa o banco de dados
Base.metadata.create_all(bind=engine)

# cria as pastas se necessário

criar_pastas_necessarias()

app = FastAPI()

# Inclui as rotas
app.include_router(router)
