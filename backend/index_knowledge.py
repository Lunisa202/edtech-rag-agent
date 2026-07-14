import os
import glob
import csv
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Load environment variables from .env file
load_dotenv()

def build_knowledge_base():
    """
    Builds a vector store from PDF manuals and structured CSV course data.
    """
    print("🚀 Starting optimized indexing process...")
    documents = []
    
    # 1. Load PDFs (Narrative documentation)
    print("📚 Processing PDF files...")
    pdf_loader = PyPDFDirectoryLoader("data")
    pdf_docs = pdf_loader.load()
    for doc in pdf_docs:
        doc.metadata['source_type'] = 'manual'
        documents.append(doc)
    
    # 2. Load CSVs intelligently (Structured data)
   # 2. Procesar CSVs de forma dinámica
    print("📊 Procesando CSVs...")
    for file_path in glob.glob("data/*.csv"):
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Esto es universal: toma todos los campos del encabezado
                # y los convierte en una oración descriptiva automáticamente.
                description = ", ".join([f"{key}: {value}" for key, value in row.items() if value])
                
                # Guardamos como Documento
                documents.append(Document(page_content=description, metadata=row))

    # 3. Intelligent Chunking
    # Chunk size increased to 1500 to keep course syllabi intact
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=300)
    fragments = text_splitter.split_documents(documents)

    print(f"✂️ Total fragments generated: {len(fragments)}")

    # 4. Embedding and Vector Store creation
    print("🧠 Creating vector database...")
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
    vector_db = FAISS.from_documents(fragments, embeddings)
    
    # Save the index locally
    vector_db.save_local("faiss_index")
    
    print("🎉 Knowledge base successfully indexed!")

if __name__ == "__main__":
    build_knowledge_base()