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

# Exponer el puerto interno del contenedor
EXPOSE 8000

# Comando de arranque:
# - Primero aplica migraciones.
# - Luego inicia ASGI con Daphne (requerido para WebSockets/Channels).
# Coolify inyecta $PORT.
# DJANGO_SETTINGS_MODULE y demás variables se definen como Secrets en Coolify.
CMD ["sh", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p ${PORT:-8000} conf.asgi:application"]
