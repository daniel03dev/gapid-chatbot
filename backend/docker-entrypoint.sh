#!/bin/bash
set -e

echo "🔧 Iniciando entrypoint de Django..."

# Esperar a que PostgreSQL esté listo (si está disponible)
if [ -n "$DB_HOST" ]; then
    echo "⏳ Esperando a PostgreSQL en $DB_HOST:$DB_PORT..."
    # Usar timeout + /dev/tcp en lugar de nc (que podría no estar instalado)
    timeout=30
    while [ $timeout -gt 0 ]; do
        if python3 -c "import socket; socket.create_connection(('$DB_HOST', $DB_PORT), timeout=2)" 2>/dev/null; then
            echo "✓ PostgreSQL está listo"
            break
        fi
        echo "   Reintentando... ($timeout segundos restantes)"
        sleep 1
        timeout=$((timeout - 1))
    done
    
    if [ $timeout -le 0 ]; then
        echo "⚠️  Timeout esperando PostgreSQL, continuando de todas formas..."
    fi
fi

# Ejecutar migraciones
echo "🗂️  Ejecutando migraciones..."
python manage.py migrate --noinput

# Crear superusuario si no existe (opcional)
echo "👤 Verificando superusuario..."
python manage.py shell << END
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("✓ Superusuario 'admin' creado")
else:
    print("✓ Superusuario ya existe")
END

echo "✅ Entrypoint completado"

# Ejecutar comando pasado como argumento
exec "$@"
