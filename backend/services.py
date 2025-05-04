# backend/services.py
import pytesseract
from PIL import Image
from langchain.document_loaders import PyPDFLoader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text(file_path):
    """Extract text from PDF or image file."""
    logger.info(f"Extracting text from: {file_path}")
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        return " ".join([p.page_content for p in pages])
    elif file_path.endswith((".jpg", ".png")):
        image = Image.open(file_path)
        return pytesseract.image_to_string(image).strip()
    logger.warning(f"Unsupported file type: {file_path}")
    return None