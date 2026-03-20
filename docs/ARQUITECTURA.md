# Arquitectura del Sistema GAPID Chatbot

## 🎯 Visión General

GAPID Chatbot es un sistema conversacional inteligente basado en **Recuperación de Información Aumentada (RAG)** que facilita el acceso a información sobre la Plataforma para la Gestión Administrativa del Sistema de Programas y Proyectos (GAPID) de Cuba.

## 🏗️ Componentes Principales

### 1. **Backend Django + DRF**

**Ubicación**: `backend/`

- **Framework**: Django 5.1.0 + Django REST Framework 3.14.0
- **Base de Datos**: PostgreSQL 14
- **Puertos**: 8000

#### Módulos:

- **`models.py`**: Modelos ORM
  - `Conversation`: Sesión de chat del usuario
  - `Message`: Mensaje individual en una conversación

- **`serializers.py`**: Serializadores DRF
  - `MessageSerializer`: Serialización de mensajes
  - `ConversationListSerializer`: Lista sin mensajes anidados
  - `ConversationDetailSerializer`: Detalles con mensajes

- **`views.py`**: Vistas REST
  - `ConversationListCreateView`: GET/POST conversaciones
  - `ConversationDetailView`: GET/PUT/DELETE conversación
  - `MessageListCreateView`: GET/POST mensajes

- **`services/`**: Servicios de lógica de negocio
  - `document_processor.py`: Carga y chunking de documentos
  - `vectorizer.py`: Vectorización con sentence-transformers + FAISS
  - `chat_service.py`: Coordinador RAG principal

- **`management/commands/build_index.py`**: Comando para indexar documentos

#### Endpoints API:

```
GET    /api/status/                          # Health check
GET    /api/conversations/                   # Listar conversaciones
POST   /api/conversations/                   # Crear conversación
GET    /api/conversations/<id>/              # Obtener conversación
PUT    /api/conversations/<id>/              # Actualizar conversación
DELETE /api/conversations/<id>/              # Eliminar conversación
GET    /api/conversations/<id>/messages/     # Listar mensajes
POST   /api/conversations/<id>/messages/     # Crear mensaje
```

### 2. **Frontend Next.js + TypeScript**

**Ubicación**: `frontend/`

- **Framework**: Next.js 14 + React 18
- **Lenguaje**: TypeScript 5.3
- **Cliente HTTP**: Axios
- **Puertos**: 3000

#### Estructura:

```
src/
├── components/          # Componentes React reutilizables
│   ├── Chat.tsx        # Componente principal de chat
│   ├── ChatMessage.tsx # Renderiza mensajes individuales
│   └── ChatInput.tsx   # Input de texto y envío
├── pages/              # Páginas Next.js
│   ├── _app.tsx       # Aplicación raíz
│   └── index.tsx      # Página principal
├── services/
│   └── api.ts         # Cliente Axios y funciones API
├── types/
│   └── index.ts       # Tipos TypeScript del dominio
└── styles/
    ├── Chat.module.css # Estilos del chat
    └── globals.css    # Estilos globales
```

#### Características:

- Componente Chat con gestión de estado
- Burbujas de mensajes con diferenciación usuario/asistente
- Input con soporte Enter para enviar
- Auto-scroll al final de mensajes
- Indicador de carga
- Manejo de errores

### 3. **Base de Datos PostgreSQL**

**Contenedor**: `postgres:14-alpine`
**Puerto**: 5432

#### Schema:

```sql
-- Conversaciones
CREATE TABLE chatbot_conversation (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Mensajes
CREATE TABLE chatbot_message (
  id SERIAL PRIMARY KEY,
  conversation_id INTEGER FOREIGN KEY,
  role VARCHAR(10), -- 'user' o 'assistant'
  content TEXT,
  created_at TIMESTAMP,
  INDEX (conversation_id, created_at)
);
```

### 4. **Sistema RAG (Retrieval-Augmented Generation)**

#### Flujo:

1. **Document Processing**
   - Lee archivos `.txt` de `data/documents/`
   - Divide en chunks de 500 caracteres con 100 de overlap
   - Mantiene metadatos (fuente, chunk_id)

2. **Vectorización**
   - Modelo: `paraphrase-multilingual-MiniLM-L12-v2` (sentence-transformers)
   - Genera embeddings de 384 dimensiones
   - Indexa con FAISS (Flat L2)

3. **Búsqueda Semántica**
   - Query → Embedding
   - Top-k búsqueda en FAISS
   - Retorna chunks relevantes

4. **Generación de Respuesta**
   - Construye contexto desde chunks
   - Retorna respuesta + fuentes + confidence_score

#### Archivos Clave:

- `data/documents/`: Documentos fuente (.txt)
- `data/vectors/`: Índice FAISS persistido

## 🔄 Flujo de Datos

```
┌─────────────────────────────────────────────────────────┐
│  Usuario escribe en el Frontend (Next.js)               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ API Call (Axios)           │
        │ POST /api/messages/        │
        └────────────┬───────────────┘
                     │
                     ▼
    ┌────────────────────────────────────┐
    │ Backend Django REST API            │
    │ MessageListCreateView              │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │ ChatService.answer_question()      │
    │ 1. Vectoriza query                 │
    │ 2. Busca en FAISS                  │
    │ 3. Genera respuesta                │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │ Guarda respuesta en DB             │
    │ PostgreSQL (Message.assistant)     │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │ Retorna JSON con respuesta         │
    └────────────┬───────────────────────┘
                 │
                 ▼
        ┌────────────────────────────┐
        │ Frontend actualiza UI       │
        │ Renderiza ChatMessage       │
        └────────────────────────────┘
```

## 📦 Dependencias Principales

### Backend

```
Django==5.1.0
djangorestframework==3.14.0
psycopg2-binary==2.9.9
sentence-transformers==3.0.1
faiss-cpu==1.8.0
numpy==1.24.3
python-dotenv==1.0.1
```

### Frontend

```
next==14.1.0
react==18.3.0
react-dom==18.3.0
axios==1.6.5
typescript==5.3.3
```

## 🐳 Contenedorización

### Docker Compose

3 servicios orquestados:

1. **db**: PostgreSQL 14
   - Volumen persistente: `postgres_data:/var/lib/postgresql/data`
   - Health check cada 10s

2. **backend**: Django
   - Build desde `backend/Dockerfile`
   - Volúmenes: código y data
   - Ejecuta migraciones automáticamente

3. **frontend**: Next.js
   - Build desde `frontend/Dockerfile`
   - Dev mode con hot reload
   - Depende de backend

### Red

`gapid-network`: Bridge network para comunicación entre servicios

## 🔐 Variables de Entorno

Ver `.env.example`:

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `DB_HOST`, `DB_PORT`
- `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`
- `NEXT_PUBLIC_API_URL`

## 📊 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    Cliente                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Browser (http://localhost:3000)                │   │
│  │  ┌───────────────────────────────────────────┐  │   │
│  │  │ Next.js Frontend (React Components)       │  │   │
│  │  │ ├─ Chat.tsx                               │  │   │
│  │  │ ├─ ChatMessage.tsx                        │  │   │
│  │  │ └─ ChatInput.tsx                          │  │   │
│  │  └───────────┬───────────────────────────────┘  │   │
│  └──────────────┼──────────────────────────────────┘   │
└─────────────────┼──────────────────────────────────────┘
                  │
          Axios HTTP/REST
                  │
        ┌─────────▼──────────────────────┐
        │  Backend (http://localhost:8000) │
        │  ┌────────────────────────────┐  │
        │  │ Django REST Framework      │  │
        │  │ ├─ ConversationViews       │  │
        │  │ └─ MessageViews            │  │
        │  ├────────────────────────────┤  │
        │  │ Services                   │  │
        │  │ ├─ ChatService             │  │
        │  │ ├─ VectorizerService       │  │
        │  │ └─ DocumentProcessor       │  │
        │  ├────────────────────────────┤  │
        │  │ Índice FAISS (embeddings)  │  │
        │  └────────────┬───────────────┘  │
        └───────────────┼──────────────────┘
                        │
                  Database ORM
                        │
        ┌───────────────▼──────────────┐
        │  PostgreSQL (localhost:5432) │
        │  ├─ chatbot_conversation     │
        │  └─ chatbot_message          │
        └──────────────────────────────┘
```

## 🚀 Flujo de Inicio

1. `docker-compose up --build`
2. PostgreSQL inicia con healthcheck
3. Backend espera a PostgreSQL
4. Backend ejecuta migraciones
5. Frontend inicia en modo dev
6. Acceder a `http://localhost:3000`

## 📝 Comandos Útiles

```bash
# Construir índice
docker-compose exec backend python manage.py build_index

# Acceder a shell Django
docker-compose exec backend python manage.py shell

# Ver logs
docker-compose logs -f backend

# Reiniciar servicios
docker-compose restart
```

## 🔄 Ciclo de Desarrollo

1. **Backend**: Editar código en `backend/` → Hot reload
2. **Frontend**: Editar código en `frontend/` → Next.js dev server
3. **DB**: Cambios persistidos en volumen
4. **Commit**: Agregar cambios, hacer push

## 📚 Documentos Fuente (RAG)

1. **GOC-2025-O13.txt**: Reglamento del Sistema
2. **Guia_TRL.txt**: Niveles de Madurez Tecnológica
3. **Manual_SPP.txt**: Manual de Gestión del Sistema

Colocar en: `backend/data/documents/`

## ✅ Estado Actual

- ✅ Modelos y migraciones
- ✅ APIs REST completas
- ✅ Servicios de procesamiento y vectorización
- ✅ Componentes frontend
- ✅ Docker Compose
- ⏳ Integración RAG completa (requiere documentos)
- ⏳ LLM para generación mejorada de respuestas

---

**Última actualización**: Febrero 2026
**Versión**: 1.0.0 (MVP)
