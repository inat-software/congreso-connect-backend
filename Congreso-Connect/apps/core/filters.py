from django_filters import rest_framework as filters


class ActiveFilterMixin(filters.FilterSet):
    """
    Mixin que agrega filtro por campo is_active.
    Reutilizable en cualquier modelo que tenga is_active.
    """
    is_active = filters.BooleanFilter(field_name='is_active')
