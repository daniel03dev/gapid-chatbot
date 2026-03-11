"""
Servicio de chat que coordina la respuesta a consultas del usuario.
Integra procesamiento de documentos, vectorización y lógica de respuesta.
"""

import time
import re
import unicodedata
from pathlib import Path
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

    @staticmethod
    def _normalize_text(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _simplify_for_match(text: str) -> str:
        normalized = ChatService._normalize_text(text)
        normalized = re.sub(r"^\d+(?:\.\d+)*\.?\s*", "", normalized)
        normalized = normalized.strip("¿? ")
        normalized = unicodedata.normalize("NFKD", normalized)
        normalized = "".join(char for char in normalized if not unicodedata.combining(char))
        return normalized.lower()

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        words = re.findall(r"[a-zA-ZáéíóúñÁÉÍÓÚÑ0-9]+", text.lower())
        stopwords = {
            "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al",
            "y", "o", "u", "en", "por", "para", "con", "sin", "que", "se", "es", "son",
            "como", "qué", "que", "cual", "cuál", "cuando", "cuándo", "donde", "dónde",
            "a", "ante", "bajo", "cabe", "contra", "desde", "durante", "entre", "hacia",
            "hasta", "mediante", "según", "segun", "sobre", "tras", "su", "sus", "tu", "tus"
        }
        return [word for word in words if len(word) > 2 and word not in stopwords]

    @staticmethod
    def _repair_mojibake(text: str) -> str:
        if not text:
            return text

        if not re.search(r"Ã.|Â.|â€|â€™|â€œ|â€", text):
            return text

        for source_encoding in ("latin-1", "cp1252"):
            try:
                repaired = text.encode(source_encoding).decode("utf-8")
                if repaired.count("Ã") < text.count("Ã"):
                    return repaired
            except Exception:
                continue

        return text

    def _load_source_document(self, source_name: str) -> str:
        try:
            document_path = Path(self.documents_dir) / source_name
            if not document_path.exists():
                return ""
            return self.processor._read_text_with_fallback(document_path)
        except Exception:
            return ""

    def _looks_like_heading(self, line: str) -> bool:
        clean = self._normalize_text(line)
        if not clean:
            return False

        if re.match(r"^\d+(\.\d+)*\.?\s+", clean):
            return True

        if clean.endswith("?"):
            return True

        if clean.isupper() and len(clean.split()) <= 12:
            return True

        return False

    def _cleanup_explanation(self, text: str, query: str) -> str:
        explanation = self._normalize_text(self._repair_mojibake(text))
        if not explanation:
            return ""

        sentences = [
            self._normalize_text(sentence)
            for sentence in re.split(r"(?<=[.!?])\s+", explanation)
            if self._normalize_text(sentence)
        ]

        filtered = []
        seen = set()
        query_lower = query.lower()
        query_tokens = set(self._tokenize(query))

        for sentence in sentences:
            sentence_lower = sentence.lower()

            if re.match(r"^[A-Z]{2,6}\s*\([^\)]*\)\s*:\s*", sentence):
                if "trl" not in sentence_lower:
                    continue

            sentence_tokens = set(self._tokenize(sentence))
            if query_tokens and filtered:
                overlap = len(sentence_tokens.intersection(query_tokens))
                if overlap == 0 and len(sentence) < 80:
                    continue

            key = sentence_lower.strip(" .")
            if key in seen:
                continue

            redundant = False
            for kept in filtered:
                kept_key = kept.lower().strip(" .")
                if key in kept_key or kept_key in key:
                    redundant = True
                    break

            if redundant:
                continue

            seen.add(key)
            filtered.append(sentence)

            if len(" ".join(filtered)) >= 650:
                break

        explanation = " ".join(filtered) if filtered else explanation

        if not re.search(r"[.!?]$", explanation):
            last_complete_sentence = re.search(r"^(.*[.!?])\s+[^.!?]*$", explanation)
            if last_complete_sentence:
                explanation = last_complete_sentence.group(1).strip()
            else:
                explanation = explanation.rstrip(" ,;:") + "."

        return self._repair_mojibake(explanation)

    def _extract_section_passage(self, query: str, source_name: str) -> str:
        document_text = self._load_source_document(source_name)
        if not document_text:
            return ""

        lines = document_text.splitlines()
        query_clean = self._simplify_for_match(query)

        def should_skip_line(line: str) -> bool:
            clean = self._normalize_text(line)
            if not clean:
                return True
            if "." in clean and clean.count(".") >= 10:
                return True
            if clean in {"1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9."}:
                return True
            if "Av. Faro" in clean or "Guadalajara, Jalisco" in clean or "Tel.:" in clean:
                return True
            return False

        for index, line in enumerate(lines):
            clean_line = self._normalize_text(line)
            if self._simplify_for_match(clean_line) != query_clean:
                continue

            collected = []
            for next_line in lines[index + 1:]:
                if should_skip_line(next_line):
                    if collected and len(" ".join(collected)) >= 220:
                        break
                    continue

                if collected and self._looks_like_heading(next_line):
                    break

                collected.append(self._normalize_text(next_line))

                if len(" ".join(collected)) >= 700:
                    break

            passage = self._cleanup_explanation(" ".join(collected), query)
            if passage:
                return passage

        return ""

    def _extract_chunk_passage(self, query: str, context_chunks: List[dict], source_name: str) -> str:
        query_tokens = set(self._tokenize(query))
        candidate_sentences = []

        for chunk in context_chunks:
            if chunk.get("source") != source_name:
                continue

            text = self._repair_mojibake(chunk.get("text", ""))
            text = re.sub(r"\s*\|\s*", "\n", text)

            for raw_sentence in re.split(r"(?<=[.!?])\s+|\n+", text):
                sentence = self._normalize_text(raw_sentence)
                if not sentence or self._looks_like_heading(sentence):
                    continue

                tokens = set(self._tokenize(sentence))
                overlap = len(tokens.intersection(query_tokens))
                if overlap == 0 and candidate_sentences:
                    continue

                score = overlap * 10 - abs(len(sentence) - 180) / 30
                candidate_sentences.append((score, sentence))

        candidate_sentences.sort(key=lambda item: item[0], reverse=True)
        explanation = " ".join(sentence for _, sentence in candidate_sentences[:4])
        return self._cleanup_explanation(explanation, query)
    
    def generate_response(self, query: str, context_chunks: List[dict]) -> Tuple[str, Optional[str]]:
        """
        Genera una respuesta basada en el contexto.
        Busca un bloque coherente en el documento fuente y devuelve una respuesta
        natural, breve y útil para el usuario.
        
        Args:
            query: Pregunta del usuario.
            context_chunks: Chunks relevantes.

        Returns:
            Tupla con (respuesta del asistente, fuente principal sugerida).
        """
        if not context_chunks:
            return "No encontré información relevante para responder tu pregunta.", None

        primary_source = context_chunks[0].get("source", "Documento sin nombre")

        explanation = self._extract_section_passage(query, primary_source)
        if not explanation:
            explanation = self._extract_chunk_passage(query, context_chunks, primary_source)

        if not explanation:
            return (
                f"No encontré información suficiente para responder de forma precisa.\n\nFuente sugerida: {primary_source}.",
                primary_source,
            )

        return f"{explanation}\n\nFuente sugerida: {primary_source}.", primary_source
    
    def answer_question(self, query: str, k: int = 3, log_to_db: bool = False, 
                       conversation_id: Optional[int] = None,
                       request_meta: Optional[dict] = None) -> dict:
        """
        Responde una pregunta del usuario.
        
        Args:
            query: Pregunta del usuario.
            k: Número de chunks para contexto.
            log_to_db: Si True, registra la consulta en la BD.
            conversation_id: ID de la conversación (para logging).
            request_meta: Metadata del request (IP, user-agent, etc).
            
        Returns:
            Dict con 'answer', 'sources', 'response_time', 'chunks_retrieved'.
        """
        start_time = time.time()
        
        if not self.is_indexed:
            return {
                "answer": "Sistema no indexado. Por favor, ejecuta 'build_index' primero.",
                "sources": [],
                "response_time": 0.0,
                "chunks_retrieved": 0
            }
        
        # Obtener contexto relevante
        results = self.get_context(query, k=k)
        context_chunks = [chunk for chunk, _ in results]
        
        # Generar respuesta
        answer, main_source = self.generate_response(query, context_chunks)

        # Recopilar solo la fuente principal sugerida
        sources = [main_source] if main_source else []
        
        # Calcular tiempo de respuesta
        response_time = time.time() - start_time
        
        result = {
            "answer": answer,
            "sources": sources,
            "confidence_score": float(1.0 - (sum([d for _, d in results]) / k / 100)),
            "response_time": response_time,
            "chunks_retrieved": len(context_chunks)
        }
        
        # Registrar en BD si se solicita
        if log_to_db:
            self._log_query_to_db(
                query=query,
                answer=answer,
                context_chunks=context_chunks,
                response_time=response_time,
                conversation_id=conversation_id,
                request_meta=request_meta
            )
        
        return result
    
    def _log_query_to_db(self, query: str, answer: str, context_chunks: List[dict],
                        response_time: float, conversation_id: Optional[int] = None,
                        request_meta: Optional[dict] = None):
        """
        Registra una consulta en la base de datos.
        
        Args:
            query: Pregunta del usuario.
            answer: Respuesta generada.
            context_chunks: Chunks utilizados.
            response_time: Tiempo de respuesta en segundos.
            conversation_id: ID de la conversación.
            request_meta: Metadata del request (IP, user-agent).
        """
        try:
            from ..models import QueryLog, Conversation
            
            # Extraer contexto usado
            context_used = "\n\n---\n\n".join([
                f"[{chunk['source']}]\n{chunk['text']}"
                for chunk in context_chunks
            ])
            
            # Obtener conversación si existe
            conversation = None
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                except Conversation.DoesNotExist:
                    pass
            
            # Extraer metadata del request
            ip_address = None
            user_agent = ""
            if request_meta:
                ip_address = request_meta.get('ip_address')
                user_agent = request_meta.get('user_agent', '')
            
            # Crear registro
            QueryLog.objects.create(
                conversation=conversation,
                user_query=query,
                assistant_response=answer,
                response_time=response_time,
                chunks_retrieved=len(context_chunks),
                context_used=context_used,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
        except Exception as e:
            # No fallar si el logging falla
            print(f"⚠️ Error al registrar query en BD: {e}")
    
    @staticmethod
    def log_audit_event(event_type: str, description: str, 
                       severity: str = 'info', metadata: Optional[dict] = None,
                       request_meta: Optional[dict] = None):
        """
        Registra un evento de auditoría.
        
        Args:
            event_type: Tipo de evento (query, index_build, error, etc).
            description: Descripción del evento.
            severity: Nivel de severidad (info, warning, error, critical).
            metadata: Datos adicionales en formato dict.
            request_meta: Metadata del request (IP, user-agent).
        """
        try:
            from ..models import AuditLog
            
            # Extraer metadata del request
            ip_address = None
            user_agent = ""
            if request_meta:
                ip_address = request_meta.get('ip_address')
                user_agent = request_meta.get('user_agent', '')
            
            AuditLog.objects.create(
                event_type=event_type,
                description=description,
                severity=severity,
                metadata=metadata or {},
                ip_address=ip_address,
                user_agent=user_agent
            )
            
        except Exception as e:
            print(f"⚠️ Error al registrar evento de auditoría: {e}")
