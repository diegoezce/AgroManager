from django.contrib import admin
from .models import Animal, PastureZone, GrowthRecord, HealthRecord, SalePrediction, WeatherRecord

# Registramos cada modelo
admin.site.register(Animal)
admin.site.register(PastureZone)
admin.site.register(GrowthRecord)
admin.site.register(HealthRecord)
admin.site.register(SalePrediction)
admin.site.register(WeatherRecord)