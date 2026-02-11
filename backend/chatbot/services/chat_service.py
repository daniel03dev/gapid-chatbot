"""
Servicio de chat que coordina la respuesta a consultas del usuario.
Integra procesamiento de documentos, vectorización y lógica de respuesta.
"""

from typing import List, Tuple, Optional
from .document_processor import DocumentProcessor
from .vectorizer import VectorizerService


class ChatService:
    """Coordina la respuesta a consultas del usuario usando RAG."""
    
    def __init__(self, documents_dir: str = "data/documents", 
                 vectors_dir: str = "data/vectors"):
        """
        Args:
            documents_dir: Directorio con documentos .txt.
            vectors_dir: Directorio para guardar/cargar índices.
        """
        self.documents_dir = documents_dir
        self.vectors_dir = vectors_dir
        self.processor = DocumentProcessor(chunk_size=500, overlap=100)
        self.vectorizer = VectorizerService()
        self.is_indexed = False
    
    def build_index(self) -> bool:
        """
        Construye el índice de vectores desde los documentos.
        
        Returns:
            True si el indexado fue exitoso.
        """
        try:
            print("🔄 Iniciando construcción del índice...")
            
            # Cargar y procesar documentos
            chunks = self.processor.process_all_documents(self.documents_dir)
            
            if not chunks:
                print("⚠️ No hay chunks para indexar.")
                return False
            
            # Vectorizar y construir índice
            self.vectorizer.build_index(chunks)
            
            # Guardar índice
            self.vectorizer.save_index(self.vectors_dir)
            
            self.is_indexed = True
            print("✅ Índice construido y guardado exitosamente.")
            return True
            
        except Exception as e:
            print(f"❌ Error construyendo índice: {e}")
            return False
    
    def load_index(self) -> bool:
        """
        Carga un índice previamente construido.
        
        Returns:
            True si la carga fue exitosa.
        """
        try:
            self.vectorizer.load_index(self.vectors_dir)
            self.is_indexed = True
            return True
        except Exception as e:
            print(f"⚠️ No se pudo cargar índice: {e}")
            return False
    
    def get_context(self, query: str, k: int = 3) -> List[Tuple[dict, float]]:
        """
        Obtiene los chunks más relevantes para una consulta.
        
        Args:
            query: Pregunta del usuario.
            k: Número de chunks a retornar.
            
        Returns:
            Lista de (chunk, distancia).
        """
        if not self.is_indexed:
            return []
        
        return self.vectorizer.search(query, k=k)
    
    def generate_response(self, query: str, context_chunks: List[dict]) -> str:
        """
        Genera una respuesta basada en el contexto.
        (Implementación simple - puede extenderse con LLMs)
        
        Args:
            query: Pregunta del usuario.
            context_chunks: Chunks relevantes.
            
        Returns:
            Respuesta del asistente.
        """
        if not context_chunks:
            return "No encontré información relevante para responder tu pregunta."
        
        # Extraer texto de chunks
        context_text = "\n\n".join([
            f"[Fuente: {chunk['source']}]\n{chunk['text']}"
            for chunk in context_chunks
        ])
        
        # Respuesta simple (puede reemplazarse con LLM real)
        response = f"""Basándome en los documentos disponibles:

{context_text}

Para una respuesta completa y detallada, por favor consulta la documentación oficial del GAPID."""
        
        return response
    
    def answer_question(self, query: str, k: int = 3) -> dict:
        """
        Responde una pregunta del usuario.
        
        Args:
            query: Pregunta del usuario.
            k: Número de chunks para contexto.
            
        Returns:
            Dict con 'answer' y 'sources'.
        """
        if not self.is_indexed:
            return {
                "answer": "Sistema no indexado. Por favor, ejecuta 'build_index' primero.",
                "sources": []
            }
        
        # Obtener contexto relevante
        results = self.get_context(query, k=k)
        context_chunks = [chunk for chunk, _ in results]
        
        # Generar respuesta
        answer = self.generate_response(query, context_chunks)
        
        # Recopilar fuentes
        sources = list(set([chunk['source'] for chunk in context_chunks]))
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence_score": float(1.0 - (sum([d for _, d in results]) / k / 100))
        }
