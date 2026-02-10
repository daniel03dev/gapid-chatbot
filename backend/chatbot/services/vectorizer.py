"""
Servicio de vectorización.
Convierte texto en embeddings usando sentence-transformers e indexa con FAISS.
"""

import os
import pickle
from typing import List, Tuple
import numpy as np

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    faiss = None
    SentenceTransformer = None


class VectorizerService:
    """Vectoriza documentos y realiza búsquedas semánticas con FAISS."""
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Args:
            model_name: Nombre del modelo de sentence-transformers a usar.
        """
        if SentenceTransformer is None:
            raise ImportError("Instala: pip install sentence-transformers faiss-cpu")
        
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def vectorize_chunks(self, chunks: List[dict]) -> np.ndarray:
        """
        Vectoriza una lista de chunks.
        
        Args:
            chunks: Lista de dicts con campo 'text'.
            
        Returns:
            Array de embeddings (N x embedding_dim).
        """
        texts = [chunk["text"] for chunk in chunks]
        print(f"🔄 Vectorizando {len(texts)} chunks...")
        
        embeddings = self.model.encode(texts, show_progress_bar=True)
        print(f"✅ Embeddings generados: {embeddings.shape}")
        
        return embeddings
    
    def build_index(self, chunks: List[dict]) -> None:
        """
        Construye un índice FAISS a partir de chunks.
        
        Args:
            chunks: Lista de chunks procesados.
        """
        self.chunks = chunks
        embeddings = self.vectorize_chunks(chunks)
        
        # Crear índice FAISS
        print(f"🏗️  Construyendo índice FAISS...")
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(embeddings.astype(np.float32))
        print(f"✅ Índice construido con {self.index.ntotal} vectores")
    
    def search(self, query: str, k: int = 5) -> List[Tuple[dict, float]]:
        """
        Busca los k chunks más similares a una query.
        
        Args:
            query: Texto de búsqueda.
            k: Número de resultados a retornar.
            
        Returns:
            Lista de tuplas (chunk, distancia).
        """
        if self.index is None:
            raise ValueError("Índice no construido. Ejecuta build_index() primero.")
        
        # Vectorizar query
        query_embedding = self.model.encode([query])[0].astype(np.float32)
        
        # Buscar en FAISS
        distances, indices = self.index.search(
            np.array([query_embedding]), k
        )
        
        # Retornar chunks con distancias
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[int(idx)], float(distances[0][i])))
        
        return results
    
    def save_index(self, index_path: str) -> None:
        """
        Guarda el índice y los chunks en disco.
        
        Args:
            index_path: Ruta donde guardar los archivos.
        """
        os.makedirs(index_path, exist_ok=True)
        
        # Guardar índice FAISS
        faiss.write_index(self.index, os.path.join(index_path, "faiss_index.bin"))
        
        # Guardar chunks como pickle
        with open(os.path.join(index_path, "chunks.pkl"), "wb") as f:
            pickle.dump(self.chunks, f)
        
        print(f"✅ Índice guardado en {index_path}")
    
    def load_index(self, index_path: str) -> None:
        """
        Carga un índice guardado previamente.
        
        Args:
            index_path: Ruta donde están los archivos guardados.
        """
        # Cargar índice FAISS
        self.index = faiss.read_index(os.path.join(index_path, "faiss_index.bin"))
        
        # Cargar chunks
        with open(os.path.join(index_path, "chunks.pkl"), "rb") as f:
            self.chunks = pickle.load(f)
        
        print(f"✅ Índice cargado desde {index_path}")
        print(f"   Total de chunks: {len(self.chunks)}")
