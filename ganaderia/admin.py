from django.contrib import admin
from .models import Animal, PastureZone, GrowthRecord, HealthRecord, SalePrediction, WeatherRecord, Breed, Campo, WeightRecord

# Registramos cada modelo
admin.site.register(Animal)
admin.site.register(PastureZone)
admin.site.register(GrowthRecord)
admin.site.register(HealthRecord)
admin.site.register(SalePrediction)
admin.site.register(WeatherRecord)
admin.site.register(Breed)
admin.site.register(WeightRecord)

@admin.register(Campo)
class CampoAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Cambia los campos que deseas mostrar en la lista