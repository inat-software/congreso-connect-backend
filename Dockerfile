# Dockerfile para Django 6 (PostgreSQL) con Daphne (ASGI) en producción
# Base: Python 3.13 slim
FROM python:3.13-slim

# Ajustes de entorno
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/usr/local/bin:${PATH}"

# Directorio de trabajo inicial (para instalación de deps)
WORKDIR /app

# psycopg2-binary, Pillow y el resto de dependencias se instalan desde wheels,
# por lo que no se requieren paquetes de compilación del sistema.

# Copiar requirements e instalar dependencias de Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del backend
COPY . .

# Cambiar el directorio de trabajo al proyecto Django (donde viven conf/, manage.py)
# Esto asegura que el módulo 'conf.wsgi' se resuelva correctamente
WORKDIR /app/Congreso-Connect

# Recolectar archivos estáticos (admin, swagger, etc.)
RUN python manage.py collectstatic --noinput

# Dar permisos de ejecución al entrypoint
RUN chmod +x /app/entrypoint.sh

# Exponer el puerto interno del contenedor
EXPOSE 8000

# Ejecutar entrypoint (makemigrations + migrate + daphne)
# Coolify inyecta $PORT.
# DJANGO_SETTINGS_MODULE y demás variables se definen como Secrets en Coolify.
ENTRYPOINT ["/app/entrypoint.sh"]
