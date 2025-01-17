from sqlalchemy import Column, String
from app.database import Base

class PDFModel(Base):
    __tablename__ = "pdfs"

    id = Column(String, primary_key=True, index=True)
    file_name =  Column(String, index=True)
    created_at = Column(String, index=True)
