"""
Comando Django para construir el índice de vectores.
Uso: python manage.py build_index
"""

from django.core.management.base import BaseCommand
from chatbot.services.chat_service import ChatService


class Command(BaseCommand):
    help = "Construye el índice de vectores desde los documentos en data/documents/"
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--documents-dir",
            type=str,
            default="data/documents",
            help="Directorio con archivos .txt",
        )
        parser.add_argument(
            "--vectors-dir",
            type=str,
            default="data/vectors",
            help="Directorio para guardar índices",
        )
    
    def handle(self, *args, **options):
        documents_dir = options["documents_dir"]
        vectors_dir = options["vectors_dir"]
        
        self.stdout.write(
            self.style.SUCCESS(f"📁 Documentos: {documents_dir}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"📁 Vectores: {vectors_dir}")
        )
        
        # Crear servicio y construir índice
        chat_service = ChatService(
            documents_dir=documents_dir,
            vectors_dir=vectors_dir
        )
        
        success = chat_service.build_index()
        
        if success:
            self.stdout.write(
                self.style.SUCCESS("✅ Índice construido exitosamente")
            )
        else:
            self.stdout.write(
                self.style.ERROR("❌ Error al construir el índice")
            )
