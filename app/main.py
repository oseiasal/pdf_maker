from fastapi import FastAPI
from app.routes import router
from app.database import Base, engine

# Inicializa o banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Inclui as rotas
app.include_router(router)
