from django.db import models
from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFilter(filters.FilterSet):
    """Filtros para el listado de usuarios."""
    search = filters.CharFilter(method='filter_search', label='Buscar')
    role = filters.ChoiceFilter(choices=User.Role.choices)
    is_active = filters.BooleanFilter()

    class Meta:
        model = User
        fields = ['role', 'is_active']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(email__icontains=value)
            | models.Q(first_name__icontains=value)
            | models.Q(last_name__icontains=value)
        )
