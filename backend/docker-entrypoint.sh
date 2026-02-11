#!/bin/bash
set -e

echo "🔧 Iniciando entrypoint de Django..."

# Esperar a que PostgreSQL esté listo (si está disponible)
if [ -n "$DB_HOST" ]; then
    echo "⏳ Esperando a PostgreSQL en $DB_HOST:$DB_PORT..."
    while ! nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; do
        echo "   Reintentando..."
        sleep 1
    done
    echo "✓ PostgreSQL está listo"
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
