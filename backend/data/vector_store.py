# vector_store.py
import os
import chromadb
from chromadb.config import Settings

class VectorStore:
    def __init__(self):
        # Initialize ChromaDB client
        persist_directory = os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db")
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            chroma_db_impl="duckdb+parquet",
        ))
    
    def create_collection(self, name):
        """Create a new collection or get existing one"""
        return self.client.get_or_create_collection(name=name)
    
    def add_documents(self, collection_name, documents, metadatas=None, ids=None):
        """Add documents to a collection"""
        collection = self.create_collection(collection_name)
        
        if ids is None:
            # Generate simple IDs based on position
            ids = [f"doc_{i}" for i in range(len(documents))]
            
        if metadatas is None:
            # Create empty metadata for each document
            metadatas = [{} for _ in documents]
            
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    def query(self, collection_name, query_text, n_results=5):
        """Query documents from a collection"""
        collection = self.create_collection(collection_name)
        
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        return results