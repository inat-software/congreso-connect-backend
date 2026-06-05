from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """
    Paginacion estandar del proyecto.
    Permite al cliente controlar el tamano de pagina via query param.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargePagination(PageNumberPagination):
    """
    Paginacion para listados grandes (ej: respuestas de encuestas).
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
