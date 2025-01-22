
from fastapi import APIRouter
from .make_pdf import pdf_router 
from .remove_bg import bg_router 

router = APIRouter()

# Incluindo as rotas dos módulos
router.include_router(bg_router,  tags=["Background Removal"])
router.include_router(pdf_router,  tags=["PDF Maker"])