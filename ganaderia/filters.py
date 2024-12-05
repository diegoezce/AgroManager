import django_filters
from .models import Animal, Breed

class AnimalFilter(django_filters.FilterSet):
    # Filtro para la especie (búsqueda parcial)
    species = django_filters.CharFilter(lookup_expr='icontains')
    
    # Filtro para la raza, usando el nombre de la raza (campo 'name' de Breed)
    breed = django_filters.CharFilter(field_name='breed__name', lookup_expr='icontains')
    
    # Filtro para el estado de salud (búsqueda parcial)
    health_status = django_filters.CharFilter(lookup_expr='icontains')
    
    # Filtro para el rango de fechas de nacimiento
    birth_date = django_filters.DateFromToRangeFilter()
    
    class Meta:
        model = Animal
        fields = ['species', 'breed', 'health_status', 'birth_date']