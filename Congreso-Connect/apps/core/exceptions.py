from rest_framework.exceptions import APIException
from rest_framework import status


class BusinessLogicError(APIException):
    """
    Excepcion para errores de logica de negocio.
    Retorna 400 Bad Request con un mensaje descriptivo.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error en la logica de negocio.'
    default_code = 'business_logic_error'


class ResourceNotFoundError(APIException):
    """
    Excepcion cuando un recurso no existe o no esta disponible.
    Retorna 404 Not Found.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Recurso no encontrado.'
    default_code = 'not_found'
