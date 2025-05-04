# backend/main.py
from fastapi import FastAPI, UploadFile, File, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import os
import shutil
from backend.database import get_db, init_db
from backend.crud import save_uploaded_file
from backend.rag import answer_query, update_vector_store
from backend.services import extract_text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic model for chat request
class ChatRequest(BaseModel):
    query: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application and initializing database")
    try:
        init_db()
        logger.info("Database initialization completed successfully")
        from sqlalchemy import inspect
        from backend.database import engine
        inspector = inspect(engine)
        if 'medical_reports' in inspector.get_table_names():
            logger.info("Table 'medical_reports' exists")
        else:
            logger.error("Table 'medical_reports' does not exist")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    yield
    logger.info("Shutting down application")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data", exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), db=Depends(get_db)):
    file_location = f"data/{file.filename}"
    logger.info(f"Saving file: {file_location}")
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file_content = extract_text(file_location)
    if not file_content:
        logger.error("Failed to extract content from file")
        return JSONResponse(status_code=400, content={"message": "Failed to extract content from file."})
    new_report = save_uploaded_file(db, file_content, file.filename)
    logger.info(f"Saved report to database: {new_report.filename}")
    update_vector_store(file_location)
    return JSONResponse(content={"message": "File uploaded and processed successfully!", "filename": file.filename})

@app.post("/chat/")
async def chat(request: Request, chat_request: ChatRequest, db=Depends(get_db)):
    # Log raw request body for debugging
    raw_body = await request.body()
    logger.info(f"Raw request body: {raw_body}")
    
    query = chat_request.query
    logger.info(f"Received chat query: {query}")
    response = answer_query(query, db)
    return JSONResponse(content={"response": response})