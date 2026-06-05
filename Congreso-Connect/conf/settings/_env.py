"""
Configuracion del entorno: BASE_DIR y lectura de variables de entorno.
Modulo interno del paquete de settings.
"""

from pathlib import Path

from decouple import Config, RepositoryEnv

# BASE_DIR apunta al directorio que contiene manage.py
# __file__ -> conf/settings/_env.py
# .parent  -> conf/settings/
# .parent  -> conf/
# .parent  -> Congreso-Connect/ (raiz del proyecto con manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# .env esta al mismo nivel que manage.py
env_file = BASE_DIR / '.env'
# Fallback: si no existe .env, usar AutoConfig para leer variables del entorno del contenedor
try:
    config = Config(RepositoryEnv(str(env_file)))
except FileNotFoundError:
    from decouple import AutoConfig
    config = AutoConfig()

__all__ = ['BASE_DIR', 'config']
