"""
Servicio de generacion de QR y envio por correo del codigo del asistente.

El QR codifica SOLO el token (un UUID opaco), nunca datos personales: si alguien
ve el QR, sin el sistema no obtiene nada util. El token sirve para registrar la
asistencia al escanear en la puerta.
"""

import uuid
from io import BytesIO

import qrcode
from django.conf import settings
from django.core.mail import EmailMessage


def ensure_qr_token(user):
    """Garantiza que el usuario tenga un token QR; lo crea la primera vez."""
    if not user.qr_token:
        user.qr_token = uuid.uuid4()
        user.save(update_fields=['qr_token'])
    return user.qr_token


def generate_qr_png(data: str) -> bytes:
    """Genera la imagen PNG de un QR a partir de un texto."""
    img = qrcode.make(data)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def send_qr_email(user):
    """Envia al usuario su QR de asistente por correo (con sus datos)."""
    token = ensure_qr_token(user)
    qr_png = generate_qr_png(str(token))

    subject = 'Tu codigo QR — Muchik 2026'
    body = (
        f'Hola {user.full_name},\n\n'
        'Adjuntamos tu codigo QR para el ingreso a Muchik 2026.\n'
        'Preséntalo en la entrada del evento para registrar tu asistencia.\n\n'
        f'Nombre: {user.full_name}\n'
        f'Correo: {user.email}\n\n'
        'Nos vemos en Trujillo.'
    )

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach('qr-muchik-2026.png', qr_png, 'image/png')
    email.send(fail_silently=False)
    return token
