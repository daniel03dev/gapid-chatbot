# Guía Rápida de Inicio - GAPID Chatbot

## ⚡ 5 Minutos para Empezar

### Prerequisitos Mínimos

- Docker Desktop instalado
- Terminal/PowerShell
- Los 3 documentos en formato .txt

### Paso 1: Descargar y Preparar (2 min)

```powershell
git clone https://github.com/daniel03dev/gapid-chatbot.git
cd gapid-chatbot

# Copiar documentos .txt a:
# backend/data/documents/
# ├── GOC-2025-O13.txt
# ├── Guia_TRL.txt
# └── Manual_SPP.txt
```

### Paso 2: Iniciar Sistema (1 min)

```powershell
docker-compose up --build
```

Espera estos logs:
```
backend_1   | Starting development server at http://0.0.0.0:8000/
frontend_1  | ready - started server on 0.0.0.0:3000
```

### Paso 3: Construir Índice (2 min)

En nueva terminal:
```powershell
docker-compose exec backend python manage.py build_index
```

Espera:
```
✅ Total de chunks: XXX
✅ Índice guardado en data/vectors
```

### Paso 4: Usar el Sistema

Abre navegador en: **http://localhost:3000**

¡Listo! 🎉

---

## 🎯 Preguntas de Ejemplo

Una vez indexado, prueba:

- "¿Qué es GAPID?"
- "¿Cuáles son los niveles de madurez tecnológica?"
- "¿Cómo lleno la ficha del proyecto?"
- "¿Cuál es la diferencia entre PAP y PNAP?"

## 🛑 Detener

```powershell
docker-compose down
```

## 📖 Más Información

- Instalación detallada: `docs/INSTALACION.md`
- Arquitectura técnica: `docs/ARQUITECTURA.md`
- Backend: `backend/README.md`
- Frontend: `frontend/README.md`

---

¿Problemas? Ver sección de solución de problemas en `docs/INSTALACION.md`
