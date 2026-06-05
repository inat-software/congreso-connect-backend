"""
Script para generar una nueva SECRET_KEY de Django.
Ejecuta este script con: python generate_secret_key.py
"""
from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print(f"SECRET_KEY={secret_key}")
