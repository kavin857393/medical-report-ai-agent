# backend/rag.py
import os
import logging
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
GROQ_API_KEYS = os.getenv("GROQ_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACEHUB_API_TOKEN")

DATA_DIR = "data"
VECTOR_DB_PATH = "vectorstore"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_PATH, exist_ok=True)

def load_documents(file_path):
    logger.info(f"Loading document: {file_path}")
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = text_splitter.split_documents(documents)
    return split_docs

def create_vector_store():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    if os.path.exists(f"{VECTOR_DB_PATH}/index"):
        logger.info("Loading existing vector store")
        return FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
    logger.info("Creating new vector store")
    return FAISS.from_texts([""], embeddings)

def update_vector_store(file_path):
    global vector_store
    logger.info(f"Updating vector store with file: {file_path}")
    new_docs = load_documents(file_path)
    vector_store.add_documents(new_docs)
    vector_store.save_local(VECTOR_DB_PATH)

# Initialize vector store and retriever
vector_store = create_vector_store()
retriever = vector_store.as_retriever()

# Cache LLM
try:
    llm = ChatGroq(temperature=0.7, model_name="llama-3.1-8b-instant", api_key=GROQ_API_KEYS)
except Exception as e:
    logger.error(f"Failed to initialize ChatGroq: {str(e)}")
    raise

qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)

def answer_query(query, db):
    logger.info(f"Processing query: {query}")
    try:
        docs = retriever.get_relevant_documents(query)
        logger.info(f"Retrieved documents: {[doc.metadata for doc in docs]}")
        response = qa_chain.run(query)
        return response
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise