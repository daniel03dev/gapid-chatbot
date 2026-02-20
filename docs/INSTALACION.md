# Guía de Instalación - GAPID Chatbot

## 📋 Requisitos Previos

### Obligatorios

- **Docker Desktop** (v20.10+)
  - [Descargar para Windows](https://www.docker.com/products/docker-desktop)
  - [Descargar para Mac](https://www.docker.com/products/docker-desktop)
  - [Descargar para Linux](https://docs.docker.com/engine/install/)

- **Git** (v2.20+)
  - [Descargar Git](https://git-scm.com/download)

### Opcionales

- **VS Code** con extensiones recomendadas:
  - Remote - Containers
  - Docker
  - Python
  - Prettier

## 🚀 Instalación Paso a Paso

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/daniel03dev/gapid-chatbot.git
cd gapid-chatbot
```

### Paso 2: Preparar Documentos

Los documentos fuente son **esenciales** para que el sistema funcione.

#### 2.1 Convertir documentos a .txt

Si tus documentos están en PDF o DOCX:

**Para PDFs:**
- Abre con Adobe Reader o navegador
- Ctrl+A (selecciona todo)
- Ctrl+C (copia)
- Abre Notepad, Ctrl+V (pega)
- Ctrl+S (guarda como `.txt`)

**Para DOCX:**
- Abre en Word
- Archivo → Guardar como
- Tipo: "Texto sin formato (*.txt)"
- Encoding: UTF-8

#### 2.2 Colocar documentos

Copia los 3 archivos `.txt` a:

```
backend/data/documents/
├── GOC-2025-O13.txt
├── Guia_TRL.txt
└── Manual_SPP.txt
```

### Paso 3: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar según sea necesario (opcional para desarrollo)
# Los valores por defecto funcionan en local
```

### Paso 4: Construir e Iniciar con Docker

```bash
# Construir imágenes y iniciar servicios
docker-compose up --build
```

⏳ **Primera ejecución tarda 5-10 minutos** (descarga imágenes, instala dependencias)

**Espera a ver logs similares a:**

```
backend_1   | Django version 5.1.0, using settings 'config.settings'
backend_1   | Starting development server at http://0.0.0.0:8000/
frontend_1  | ready - started server on 0.0.0.0:3000
```

### Paso 5: Construir el Índice

**En una NUEVA terminal** (sin cerrar la anterior):

```bash
cd gapid-chatbot
docker-compose exec backend python manage.py build_index
```

Verás output como:

```
📄 Encontrados 3 archivos .txt
✓ Cargado: GOC-2025-O13.txt (98234 caracteres)
✓ Cargado: Guia_TRL.txt (45123 caracteres)
✓ Cargado: Manual_SPP.txt (156789 caracteres)

🔄 Procesando documentos...
   GOC-2025-O13.txt → 156 chunks
   Guia_TRL.txt → 78 chunks
   Manual_SPP.txt → 298 chunks

✅ Total de chunks: 532
🔄 Vectorizando 532 chunks...
✅ Embeddings generados: (532, 384)
🏗️ Construyendo índice FAISS...
✅ Índice construido con 532 vectores
✅ Índice guardado en data/vectors
```

### Paso 6: Acceder al Sistema

Abre tu navegador en:

| Componente | URL | Descripción |
|-----------|-----|-------------|
| **Frontend Chat** | http://localhost:3000 | Interfaz del chatbot |
| **Admin Django** | http://localhost:8000/admin | Panel administrativo |
| **API Status** | http://localhost:8000/api/status/ | Health check |
| **DB** | localhost:5432 | PostgreSQL (conexión interna) |

**Credenciales Admin:**
- Usuario: `admin`
- Contraseña: `admin123`

## ✅ Verificar Instalación

### 1. Frontend Funciona

Abre http://localhost:3000 y deberías ver:
- Interfaz de chat
- Input para preguntas
- Botón "Nueva Conversación"

### 2. Backend Funciona

```bash
# Terminal diferente
curl http://localhost:8000/api/status/

# Respuesta esperada:
# {"status":"ok","message":"Backend GAPID Chatbot está operacional"}
```

### 3. Base de Datos Funciona

```bash
# Ver conversaciones creadas
docker-compose exec backend python manage.py shell
>>> from chatbot.models import Conversation
>>> Conversation.objects.all().count()
```

### 4. Índice Construido

```bash
# Verificar que existe el índice
ls -la backend/data/vectors/
# Deberías ver: faiss_index.bin y chunks.pkl
```

## 🧪 Pruebas Básicas

### 1. Crear Conversación

```bash
curl -X POST http://localhost:8000/api/conversations/
```

Respuesta:
```json
{
  "id": 1,
  "created_at": "2026-02-17T10:30:00Z",
  "updated_at": "2026-02-17T10:30:00Z",
  "message_count": 0
}
```

### 2. Crear Mensaje

```bash
curl -X POST http://localhost:8000/api/conversations/1/messages/ \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": "¿Qué es GAPID?"}'
```

### 3. Listar Mensajes

```bash
curl http://localhost:8000/api/conversations/1/
```

## 🛑 Detener el Sistema

```bash
# Detener servicios (mantiene volúmenes)
docker-compose down

# Detener y eliminar volúmenes (limpia BD)
docker-compose down -v

# Ver estado
docker-compose ps
```

## 🔧 Solución de Problemas

### Puerto ya en uso

```bash
# Cambiar puerto en docker-compose.yml
# "3000:3000" → "3001:3000" (para frontend)
# "8000:8000" → "8001:8000" (para backend)
```

### Falta de espacio en disco

```bash
# Limpiar Docker
docker system prune -a --volumes
```

### PostgreSQL no conecta

```bash
# Verificar logs
docker-compose logs db

# Reiniciar servicio
docker-compose restart db
```

### Frontend no ve el backend

Verificar en `frontend/src/services/api.ts`:
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
```

Debe coincidir con la URL del backend.

### Índice no se construye

```bash
# Verificar documentos existen
ls -la backend/data/documents/

# Ver logs de error
docker-compose logs backend

# Reintentar manualmente
docker-compose exec backend python manage.py build_index --documents-dir data/documents
```

## 📊 Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs solo del backend
docker-compose logs -f backend

# Ejecutar comando en contenedor
docker-compose exec backend python manage.py shell

# Acceder a terminal del contenedor
docker-compose exec backend bash

# Rebuild después de cambios en requirements
docker-compose build --no-cache backend

# Reiniciar un servicio específico
docker-compose restart backend
```

## 🔄 Desarrollo Local

### Editar código sin reconstruir

Los volúmenes están configurados para hot reload:

```yaml
volumes:
  - ./backend:/app        # Cambios reflejados
  - ./frontend:/app       # Next.js recompila
```

**Frontend**: Los cambios se ven inmediatamente

**Backend**: Los cambios pueden requerir reinicio de Django

```bash
docker-compose restart backend
```

### Agregar nuevas dependencias

**Backend:**
```bash
# Editar backend/requirements.txt
# Luego:
docker-compose build --no-cache backend
docker-compose up backend
```

**Frontend:**
```bash
docker-compose exec frontend npm install nombre-paquete
```

## 📈 Próximos Pasos

1. **Integrar LLM**: Agregar modelo generativo para respuestas más naturales
2. **WebSocket**: Streaming de respuestas en tiempo real
3. **Auth**: Sistema de autenticación de usuarios
4. **Métricas**: Dashboard de uso del chatbot
5. **CI/CD**: Pipeline de despliegue automático

## 📞 Soporte

- 📖 Ver documentación: `docs/ARQUITECTURA.md`
- 🐛 Reportar problemas: GitHub Issues
- 💬 Discusiones: GitHub Discussions

---

**Última actualización**: Febrero 2026
**Versión**: 1.0.0
