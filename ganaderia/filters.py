import django_filters
from .models import Animal

class AnimalFilter(django_filters.FilterSet):
    class Meta:
        model = Animal
        fields = {
            'species': ['icontains'],   # Permite filtrar por especie (búsqueda parcial)
            'breed': ['exact'],         # Filtrar por raza exacta
            'health_status': ['icontains'], # Buscar por estado de salud
            'birth_date': ['gte', 'lte'],   # Filtrar por rango de fechas
        }
