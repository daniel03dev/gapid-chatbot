"""
Servicio para procesamiento de documentos.
Carga archivos .txt, los divide en chunks y los prepara para vectorización.
"""

import os
from pathlib import Path
from typing import List, Tuple


class DocumentProcessor:
    """Procesa documentos de texto y los divide en chunks."""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        """
        Args:
            chunk_size: Número de caracteres por chunk.
            overlap: Caracteres de superposición entre chunks.
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def load_documents(self, documents_dir: str) -> List[Tuple[str, str]]:
        """
        Carga todos los archivos .txt de un directorio.
        
        Args:
            documents_dir: Ruta al directorio con documentos.
            
        Returns:
            Lista de tuplas (nombre_archivo, contenido).
        """
        documents = []
        documents_path = Path(documents_dir)
        
        if not documents_path.exists():
            print(f"⚠️ Directorio {documents_dir} no existe.")
            return documents
        
        txt_files = list(documents_path.glob("*.txt"))
        print(f"📄 Encontrados {len(txt_files)} archivos .txt")
        
        for txt_file in txt_files:
            try:
                with open(txt_file, "r", encoding="utf-8") as f:
                    content = f.read()
                documents.append((txt_file.name, content))
                print(f"✓ Cargado: {txt_file.name} ({len(content)} caracteres)")
            except Exception as e:
                print(f"✗ Error cargando {txt_file.name}: {e}")
        
        return documents
    
    def chunk_document(self, content: str, document_name: str) -> List[dict]:
        """
        Divide un documento en chunks con superposición.
        
        Args:
            content: Contenido del documento.
            document_name: Nombre del archivo fuente.
            
        Returns:
            Lista de dicts con 'text', 'source' y 'chunk_id'.
        """
        chunks = []
        step = self.chunk_size - self.overlap
        
        for i in range(0, len(content), step):
            chunk_text = content[i : i + self.chunk_size]
            
            if chunk_text.strip():  # Ignorar chunks vacíos
                chunks.append({
                    "text": chunk_text,
                    "source": document_name,
                    "chunk_id": len(chunks),
                })
        
        return chunks
    
    def process_all_documents(self, documents_dir: str) -> List[dict]:
        """
        Carga y procesa todos los documentos en un directorio.
        
        Args:
            documents_dir: Ruta al directorio con documentos.
            
        Returns:
            Lista de chunks procesados.
        """
        all_chunks = []
        documents = self.load_documents(documents_dir)
        
        print(f"\n🔄 Procesando documentos...")
        for doc_name, content in documents:
            chunks = self.chunk_document(content, doc_name)
            all_chunks.extend(chunks)
            print(f"   {doc_name} → {len(chunks)} chunks")
        
        print(f"\n✅ Total de chunks: {len(all_chunks)}")
        return all_chunks
