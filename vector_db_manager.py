import os
import hashlib
from pathlib import Path
from typing import Optional, List, Tuple
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

class VectorDBManager:
    """Manages vector database operations for PDF documents"""
    
    def __init__(self, base_dir: str = "chroma_db"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.metadata_file = self.base_dir / "metadata.txt"
        
    def get_pdf_hash(self, pdf_content: bytes) -> str:
        """Generate a unique hash for PDF content"""
        return hashlib.md5(pdf_content).hexdigest()
    
    def get_db_path(self, pdf_hash: str) -> Path:
        """Get the database path for a specific PDF"""
        return self.base_dir / pdf_hash
    
    def pdf_exists(self, pdf_hash: str) -> bool:
        """Check if PDF has already been processed"""
        db_path = self.get_db_path(pdf_hash)
        return db_path.exists() and (db_path / "chroma.sqlite3").exists()
    
    def save_metadata(self, pdf_hash: str, filename: str, num_pages: int, num_chunks: int):
        """Save PDF metadata"""
        with open(self.metadata_file, 'a') as f:
            f.write(f"{pdf_hash}|{filename}|{num_pages}|{num_chunks}\n")
    
    def get_metadata(self, pdf_hash: str) -> Optional[dict]:
        """Retrieve metadata for a specific PDF"""
        if not self.metadata_file.exists():
            return None
        
        with open(self.metadata_file, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if parts[0] == pdf_hash:
                    return {
                        'hash': parts[0],
                        'filename': parts[1],
                        'num_pages': int(parts[2]),
                        'num_chunks': int(parts[3])
                    }
        return None
    
    def list_all_pdfs(self) -> List[dict]:
        """List all processed PDFs"""
        if not self.metadata_file.exists():
            return []
        
        pdfs = []
        with open(self.metadata_file, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 4:
                    pdfs.append({
                        'hash': parts[0],
                        'filename': parts[1],
                        'num_pages': int(parts[2]),
                        'num_chunks': int(parts[3])
                    })
        return pdfs
    
    def process_pdf(self, pdf_path: str, pdf_content: bytes, filename: str) -> Tuple[str, dict]:
        """
        Process a PDF and create/return vector store
        Returns: (pdf_hash, metadata)
        """
        pdf_hash = self.get_pdf_hash(pdf_content)
        
        # Check if already processed
        if self.pdf_exists(pdf_hash):
            metadata = self.get_metadata(pdf_hash)
            return pdf_hash, metadata
        
        # Load PDF
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        
        # Split documents
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = splitter.split_documents(docs)
        
        # Create vector store
        db_path = self.get_db_path(pdf_hash)
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embedding_model,
            persist_directory=str(db_path)
        )
        
        # Save metadata
        metadata = {
            'hash': pdf_hash,
            'filename': filename,
            'num_pages': len(docs),
            'num_chunks': len(chunks)
        }
        self.save_metadata(pdf_hash, filename, len(docs), len(chunks))
        
        return pdf_hash, metadata
    
    def load_vectorstore(self, pdf_hash: str) -> Optional[Chroma]:
        """Load an existing vector store"""
        if not self.pdf_exists(pdf_hash):
            return None
        
        db_path = self.get_db_path(pdf_hash)
        vectorstore = Chroma(
            persist_directory=str(db_path),
            embedding_function=self.embedding_model
        )
        return vectorstore
    
    def delete_pdf(self, pdf_hash: str) -> bool:
        """Delete a processed PDF from the database"""
        db_path = self.get_db_path(pdf_hash)
        if db_path.exists():
            import shutil
            shutil.rmtree(db_path)
            
            # Update metadata file
            if self.metadata_file.exists():
                lines = []
                with open(self.metadata_file, 'r') as f:
                    lines = [line for line in f if not line.startswith(pdf_hash)]
                with open(self.metadata_file, 'w') as f:
                    f.writelines(lines)
            return True
        return False