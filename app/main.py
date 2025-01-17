from fastapi import FastAPI
from .database import Base, engine
from .routes import router

app = FastAPI()

# Inicializar o banco de dados
Base.metadata.create_all(bind=engine)

# Registrar as rotas
app.include_router(router)
