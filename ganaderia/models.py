from django.db import models
from django.utils import timezone


class Breed(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Nombre de la raza, único
    description = models.TextField(blank=True, null=True)  # Descripción opcional de la raza

    def __str__(self):
        return self.name


class Animal(models.Model):
    identifier = models.CharField(max_length=50, unique=True)  # Ej: código de identificación único
    species = models.CharField(max_length=100)                 # Especie (vaca, toro, etc.)
    breed = models.ForeignKey(Breed, on_delete=models.SET_NULL, null=True)  # Relación a Breed
    birth_date = models.DateField()                            # Fecha de nacimiento
    weight = models.FloatField()                               # Peso en kg
    health_status = models.CharField(max_length=100)           # Estado de salud (Ej: "Saludable", "Enfermo")
    pasture_zone = models.ForeignKey('PastureZone', on_delete=models.SET_NULL, null=True)  # Zona de pastoreo actual
    is_for_sale = models.BooleanField(default=False)           # Para marcar animales listos para la venta
    date_added = models.DateTimeField(default=timezone.now)    # Fecha de registro

    def __str__(self):
        return f"{self.identifier} - {self.breed}"


# Create your models here.
class PastureZone(models.Model):
    name = models.CharField(max_length=100)                   # Nombre de la zona
    area_size = models.FloatField()                           # Tamaño en hectáreas
    grazing_capacity = models.IntegerField()                  # Capacidad de pastoreo en número de animales
    current_animals = models.ManyToManyField(Animal, blank=True, related_name='zones')  # Animales actualmente en la zona
    is_active = models.BooleanField(default=True)             # Zona activa o en descanso

    def __str__(self):
        return self.name


class GrowthRecord(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="growth_records")  # Animal asociado
    date = models.DateField()                               # Fecha de registro
    weight = models.FloatField()                            # Peso en esa fecha
    notes = models.TextField(blank=True, null=True)         # Notas adicionales (Ej: comentarios sobre salud)

    def __str__(self):
        return f"{self.animal.identifier} - {self.date}"


class HealthRecord(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="health_records")  # Animal asociado
    checkup_date = models.DateField()                         # Fecha del control de salud
    health_status = models.CharField(max_length=100)          # Estado de salud (Ej: "Saludable", "Enfermo")
    medication_given = models.CharField(max_length=100, blank=True, null=True)  # Medicación administrada
    notes = models.TextField(blank=True, null=True)           # Notas adicionales

    def __str__(self):
        return f"{self.animal.identifier} - {self.checkup_date} - {self.health_status}"


class SalePrediction(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="sale_predictions")  # Animal asociado
    predicted_sale_date = models.DateField()                     # Fecha de venta óptima sugerida
    predicted_weight = models.FloatField()                       # Peso esperado en la fecha de venta
    market_price = models.FloatField()                           # Precio de mercado estimado
    notes = models.TextField(blank=True, null=True)              # Notas adicionales

    def __str__(self):
        return f"{self.animal.identifier} - Venta sugerida: {self.predicted_sale_date}"


class WeatherRecord(models.Model):
    pasture_zone = models.ForeignKey(PastureZone, on_delete=models.CASCADE, related_name="weather_records")  # Zona de pastoreo
    date = models.DateField()                                       # Fecha del registro climático
    temperature = models.FloatField()                               # Temperatura promedio
    rainfall = models.FloatField()                                  # Precipitación en mm
    notes = models.TextField(blank=True, null=True)                 # Notas adicionales sobre el clima

    def __str__(self):
        return f"{self.pasture_zone.name} - Clima en {self.date}"


class Campo(models.Model):
    name = models.CharField(max_length=200)
    geometria = models.TextField()  # Almacena la geometría como texto (WKT o GeoJSON)

    def __str__(self):
        return self.name