# Guía de Implementación de Mejoras - AgroManager

Ejemplos de código listos para implementar basados en el análisis del proyecto.

---

## 1️⃣ FIX CRÍTICO: Seguridad - Variables de Entorno

### Paso 1: Instalar dependencia
```bash
pip install python-decouple
```

### Paso 2: Modificar `agromanager_project/settings.py`

**Antes:**
```python
SECRET_KEY = 'django-insecure-g*f2s*@va$6isvrvt0u)ssng*bh4#*s_xmqo@**!flh=-v#-1p'
DEBUG = True
ALLOWED_HOSTS = ['agrogestion-ef1971df93d0.herokuapp.com', '127.0.0.1']
```

**Después:**
```python
from decouple import config

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)  # False en producción
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])
```

### Paso 3: Crear `.env` (local)
```
SECRET_KEY=django-insecure-dev-key-for-local-development-only
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,agrogestion-ef1971df93d0.herokuapp.com
```

### Paso 4: Crear `.env.example` (para el repo)
```
SECRET_KEY=your-secure-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,yourdomain.com
```

### Paso 5: Actualizar `.gitignore`
```
.env
.env.local
.env.*.local
*.log
```

---

## 2️⃣ Validación: Crear Django Forms

### Crear `ganaderia/forms.py`

```python
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Animal, Breed, PastureZone, WeightRecord, WeatherRecord, HealthRecord


class AnimalForm(forms.ModelForm):
    """Formulario para crear/editar animales con validación."""
    
    class Meta:
        model = Animal
        fields = ['identifier', 'species', 'breed', 'birth_date', 
                  'birth_weight', 'health_status', 'pasture_zone', 'is_for_sale']
        widgets = {
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'identifier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'P.ej: AGR-001'
            }),
            'species': forms.TextInput(attrs={'class': 'form-control'}),
            'breed': forms.Select(attrs={'class': 'form-control'}),
            'birth_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'health_status': forms.TextInput(attrs={'class': 'form-control'}),
            'pasture_zone': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_identifier(self):
        identifier = self.cleaned_data.get('identifier', '').strip()
        if not identifier:
            raise ValidationError("El identificador no puede estar vacío")
        if len(identifier) < 2:
            raise ValidationError("El identificador debe tener al menos 2 caracteres")
        
        # Validar que sea único (excepto si estamos editando)
        qs = Animal.objects.filter(identifier=identifier)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un animal con este identificador")
        
        return identifier
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if not birth_date:
            raise ValidationError("La fecha de nacimiento es obligatoria")
        if birth_date > timezone.now().date():
            raise ValidationError("La fecha de nacimiento no puede ser en el futuro")
        
        from datetime import timedelta
        min_date = timezone.now().date() - timedelta(days=365*30)  # Max 30 años
        if birth_date < min_date:
            raise ValidationError("La fecha de nacimiento parece muy antigua")
        
        return birth_date
    
    def clean_birth_weight(self):
        weight = self.cleaned_data.get('birth_weight')
        if weight is None:
            raise ValidationError("El peso de nacimiento es obligatorio")
        if weight < 0:
            raise ValidationError("El peso no puede ser negativo")
        if weight > 150:  # Max para peso de nacimiento de bovino
            raise ValidationError("El peso de nacimiento parece inusualmente alto (>150kg)")
        if weight < 5:  # Min para peso de nacimiento
            raise ValidationError("El peso de nacimiento parece inusualmente bajo (<5kg)")
        return weight


class BreedForm(forms.ModelForm):
    """Formulario para crear/editar razas."""
    
    class Meta:
        model = Breed
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'P.ej: Hereford'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError("El nombre de la raza no puede estar vacío")
        
        qs = Breed.objects.filter(name=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe una raza con este nombre")
        
        return name


class WeightRecordForm(forms.ModelForm):
    """Formulario para registrar pesos."""
    
    class Meta:
        model = WeightRecord
        fields = ['weight', 'date_recorded']
        widgets = {
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Peso en kg'
            }),
            'date_recorded': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
    
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if not weight:
            raise ValidationError("El peso es obligatorio")
        if weight < 0:
            raise ValidationError("El peso no puede ser negativo")
        if weight > 1500:
            raise ValidationError("El peso parece inusualmente alto")
        return weight
    
    def clean_date_recorded(self):
        date = self.cleaned_data.get('date_recorded')
        if not date:
            raise ValidationError("La fecha es obligatoria")
        if date > timezone.now().date():
            raise ValidationError("La fecha no puede ser en el futuro")
        return date


class PastureZoneForm(forms.ModelForm):
    """Formulario para zonas de pastoreo."""
    
    class Meta:
        model = PastureZone
        fields = ['name', 'area_size', 'grazing_capacity', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'area_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'grazing_capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }
    
    def clean_area_size(self):
        area = self.cleaned_data.get('area_size')
        if area and area < 0:
            raise ValidationError("El área no puede ser negativa")
        return area


class HealthRecordForm(forms.ModelForm):
    """Formulario para registros de salud."""
    
    class Meta:
        model = HealthRecord
        fields = ['checkup_date', 'health_status', 'medication_given', 'notes']
        widgets = {
            'checkup_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'health_status': forms.TextInput(attrs={'class': 'form-control'}),
            'medication_given': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medicamentos aplicados (opcional)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)'
            }),
        }


class BulkAnimalImportForm(forms.Form):
    """Formulario para importación masiva de CSV."""
    
    file = forms.FileField(
        label='Archivo CSV',
        help_text='Soporta archivos CSV. Columnas requeridas: identifier, species, breed, birth_date, birth_weight, health_status',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            raise ValidationError("Debes seleccionar un archivo")
        
        if not file.name.endswith('.csv'):
            raise ValidationError("El archivo debe ser CSV")
        
        if file.size > 5 * 1024 * 1024:  # 5MB max
            raise ValidationError("El archivo no debe exceder 5MB")
        
        return file
```

---

## 3️⃣ Refactorizar Views - Ejemplo

### Antes (views.py original - sin validación):

```python
def create_animal(request):
    if request.method == 'POST':
        try:
            animal = Animal()
            animal.identifier = request.POST.get('identifier')
            animal.species = request.POST.get('species')
            # ... sin validación
            animal.save()
            messages.success(request, 'Datos guardados exitosamente.')
            return redirect('admin_animales')
        except Exception as e:
            messages.error(request, f'Error al guardar los datos: {e}')
            return redirect('admin_animales')
```

### Después (con Django Forms):

```python
def create_animal(request):
    """Crea un nuevo animal con validación."""
    if request.method == 'POST':
        form = AnimalForm(request.POST)
        if form.is_valid():
            animal = form.save()
            messages.success(request, f'Animal "{animal.identifier}" creado exitosamente')
            return redirect('admin_animales')
        else:
            # Los errores están en form.errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AnimalForm()
    
    context = {
        'form': form,
        'page_title': 'Crear Nuevo Animal',
    }
    return render(request, 'animal_form.html', context)


def update_animal(request, animal_id):
    """Actualiza un animal existente."""
    animal = get_object_or_404(Animal, id=animal_id)
    
    if request.method == 'POST':
        form = AnimalForm(request.POST, instance=animal)
        if form.is_valid():
            form.save()
            messages.success(request, f'Animal "{animal.identifier}" actualizado')
            return redirect('admin_animales')
    else:
        form = AnimalForm(instance=animal)
    
    context = {
        'form': form,
        'animal': animal,
        'page_title': f'Editar Animal: {animal.identifier}',
    }
    return render(request, 'animal_form.html', context)


def add_weight_record(request, animal_id):
    """Agrega un registro de peso para un animal."""
    animal = get_object_or_404(Animal, id=animal_id)
    
    if request.method == 'POST':
        form = WeightRecordForm(request.POST)
        if form.is_valid():
            weight_record = form.save(commit=False)
            weight_record.animal = animal
            weight_record.save()
            messages.success(request, f'Peso registrado: {weight_record.weight}kg')
            return redirect('admin_animales')
    else:
        form = WeightRecordForm()
    
    context = {
        'form': form,
        'animal': animal,
    }
    return render(request, 'weight_record_form.html', context)
```

---

## 4️⃣ Utilidades para Evitar Duplicación

### Crear `ganaderia/utils_models.py`

```python
"""Funciones de utilidad para manejo de modelos."""

import logging
from .models import Breed, PastureZone

logger = logging.getLogger(__name__)


def get_or_create_breed(name):
    """
    Obtiene o crea una raza de forma segura.
    
    Args:
        name (str): Nombre de la raza
        
    Returns:
        Breed: La raza creada o existente
        
    Raises:
        ValueError: Si el nombre está vacío
    """
    if not name or not name.strip():
        raise ValueError("El nombre de la raza no puede estar vacío")
    
    clean_name = name.strip()
    breed, created = Breed.objects.get_or_create(name=clean_name)
    
    if created:
        logger.info(f"Nueva raza creada: {breed.name}")
    
    return breed


def get_or_create_pasture_zone(name):
    """
    Obtiene o crea una zona de pastoreo de forma segura.
    
    Args:
        name (str): Nombre de la zona
        
    Returns:
        PastureZone: La zona creada o existente
        
    Raises:
        ValueError: Si el nombre está vacío
    """
    if not name or not name.strip():
        raise ValueError("El nombre de la zona no puede estar vacío")
    
    clean_name = name.strip()
    zone, created = PastureZone.objects.get_or_create(name=clean_name)
    
    if created:
        logger.info(f"Nueva zona de pastoreo creada: {zone.name}")
    
    return zone


def validate_animal_data(data):
    """
    Valida los datos de un animal antes de crear/actualizar.
    
    Args:
        data (dict): Datos del animal
        
    Returns:
        tuple: (es_válido, mensajes_error)
        
    Example:
        valid, errors = validate_animal_data({'identifier': '', 'breed': 'X'})
    """
    errors = []
    
    # Validar identifier
    identifier = data.get('identifier', '').strip()
    if not identifier:
        errors.append("El identificador no puede estar vacío")
    elif len(identifier) < 2:
        errors.append("El identificador debe tener al menos 2 caracteres")
    
    # Validar raza
    breed = data.get('breed', '').strip()
    if not breed:
        errors.append("La raza es obligatoria")
    
    # Validar peso
    birth_weight = data.get('birth_weight')
    if birth_weight is None or birth_weight == '':
        errors.append("El peso de nacimiento es obligatorio")
    else:
        try:
            weight = float(birth_weight)
            if weight < 0:
                errors.append("El peso no puede ser negativo")
            elif weight > 150:
                errors.append("El peso parece inusualmente alto")
        except ValueError:
            errors.append("El peso debe ser un número válido")
    
    return len(errors) == 0, errors
```

---

## 5️⃣ Logging - Configuración

### Crear `ganaderia/logging_config.py`

```python
"""Configuración de logging para AgroManager."""

import os
import logging.config

# Crear directorio de logs si no existe
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {funcName}:{lineno} - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {asctime} - {message}',
            'style': '{',
            'datefmt': '%H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'errors.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'file_animal': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'animals.log'),
            'maxBytes': 5242880,  # 5MB
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_error'],
            'level': 'INFO',
            'propagate': False,
        },
        'ganaderia': {
            'handlers': ['console', 'file_animal', 'file_error'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### En `agromanager_project/settings.py`:

```python
from ganaderia.logging_config import LOGGING_CONFIG

LOGGING = LOGGING_CONFIG
```

---

## 6️⃣ Imports Limpios - Corrección

### Antes (views.py - con duplicados):
```python
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
# ... más código
from django.shortcuts import render, get_object_or_404
from .models import Campo
# ... más código
from .models import Campo  # Duplicado
```

### Después (limpio):
```python
"""
Vistas para la aplicación de ganadería.

Maneja animal, pasture zone, breed, y gestión geoespacial.
"""

import csv
import json
import logging
from io import StringIO

import joblib
import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Avg, F, Subquery, OuterRef, Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from . import utils
from .filters import AnimalFilter
from .forms import (
    AnimalForm, BreedForm, WeightRecordForm, 
    PastureZoneForm, HealthRecordForm, BulkAnimalImportForm
)
from .models import (
    Animal, Breed, PastureZone, Campo, WeightRecord,
    GrowthRecord, HealthRecord, SalePrediction, WeatherRecord
)
from .utils import cargar_datos_geoespaciales
from .utils_models import get_or_create_breed, get_or_create_pasture_zone

logger = logging.getLogger(__name__)

# Cargar modelo ML
try:
    from .ml_loader import model_loader
except ImportError:
    logger.error("No se pudo cargar el módulo ML loader")
```

---

## 7️⃣ Tests Básicos

### Crear `ganaderia/tests/__init__.py`

```python
# Empty init file
```

### Crear `ganaderia/tests/test_models.py`

```python
"""Tests para los modelos de ganadería."""

from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta

from ..models import Animal, Breed, PastureZone, WeightRecord


class BreedModelTest(TestCase):
    """Tests para el modelo Breed."""
    
    def setUp(self):
        self.breed = Breed.objects.create(
            name='Hereford',
            description='Raza de carne roja'
        )
    
    def test_breed_str(self):
        self.assertEqual(str(self.breed), 'Hereford')
    
    def test_breed_unique_name(self):
        with self.assertRaises(Exception):
            Breed.objects.create(name='Hereford')


class AnimalModelTest(TestCase):
    """Tests para el modelo Animal."""
    
    def setUp(self):
        self.breed = Breed.objects.create(name='Angus')
        self.pasture = PastureZone.objects.create(name='Pasture A')
        self.animal = Animal.objects.create(
            identifier='AGR-001',
            species='Bovino',
            breed=self.breed,
            birth_date=date(2023, 1, 1),
            birth_weight=35.5,
            health_status='Saludable',
            pasture_zone=self.pasture
        )
    
    def test_animal_creation(self):
        self.assertEqual(self.animal.identifier, 'AGR-001')
        self.assertEqual(self.animal.species, 'Bovino')
        self.assertFalse(self.animal.is_for_sale)
    
    def test_animal_latest_weight_no_records(self):
        self.assertIsNone(self.animal.latest_weight())
    
    def test_animal_latest_weight_with_records(self):
        WeightRecord.objects.create(
            animal=self.animal,
            weight=100.0,
            date_recorded=date(2024, 1, 1)
        )
        WeightRecord.objects.create(
            animal=self.animal,
            weight=105.0,
            date_recorded=date(2024, 2, 1)
        )
        
        self.assertEqual(self.animal.latest_weight(), 105.0)
    
    def test_animal_unique_identifier(self):
        with self.assertRaises(Exception):
            Animal.objects.create(
                identifier='AGR-001',
                species='Bovino',
                breed=self.breed,
                birth_date=date(2023, 6, 1),
                birth_weight=30.0,
                health_status='Saludable'
            )


class WeightRecordTest(TestCase):
    """Tests para registros de peso."""
    
    def setUp(self):
        self.breed = Breed.objects.create(name='Hereford')
        self.animal = Animal.objects.create(
            identifier='AGR-002',
            species='Bovino',
            breed=self.breed,
            birth_date=date(2023, 1, 1),
            birth_weight=35.0,
            health_status='Saludable'
        )
    
    def test_weight_record_creation(self):
        record = WeightRecord.objects.create(
            animal=self.animal,
            weight=100.5,
            date_recorded=date(2024, 1, 15)
        )
        self.assertEqual(record.weight, 100.5)
        self.assertEqual(record.animal, self.animal)
```

### Crear `ganaderia/tests/test_views.py`

```python
"""Tests para las vistas."""

from django.test import TestCase, Client
from django.urls import reverse
from datetime import date

from ..models import Animal, Breed


class AnimalViewsTest(TestCase):
    """Tests para las vistas de animales."""
    
    def setUp(self):
        self.client = Client()
        self.breed = Breed.objects.create(name='Hereford')
        self.animal = Animal.objects.create(
            identifier='AGR-001',
            species='Bovino',
            breed=self.breed,
            birth_date=date(2023, 1, 1),
            birth_weight=35.0,
            health_status='Saludable'
        )
    
    def test_admin_animales_view(self):
        response = self.client.get(reverse('admin_animales'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AGR-001')
    
    def test_create_animal_get(self):
        response = self.client.get(reverse('create_animal'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
    
    def test_create_animal_post_valid(self):
        data = {
            'identifier': 'AGR-002',
            'species': 'Bovino',
            'breed': self.breed.id,
            'birth_date': '2023-06-01',
            'birth_weight': 38.0,
            'health_status': 'Saludable',
        }
        response = self.client.post(reverse('create_animal'), data)
        self.assertEqual(response.status_code, 302)  # Redirección
        self.assertTrue(Animal.objects.filter(identifier='AGR-002').exists())
```

---

## 8️⃣ Mejor Manejo de Importación CSV

### Mejorar `carga_bulk_animales` en `views.py`

```python
import logging
from .forms import BulkAnimalImportForm
from .utils_models import get_or_create_breed, get_or_create_pasture_zone, validate_animal_data

logger = logging.getLogger(__name__)


def carga_bulk_animales(request):
    """
    Importa múltiples animales desde un archivo CSV.
    
    El CSV debe tener las columnas:
    - identifier
    - species
    - breed
    - birth_date (formato: YYYY-MM-DD)
    - birth_weight
    - health_status
    - pasture_zone (opcional)
    """
    if request.method == 'POST':
        form = BulkAnimalImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = form.cleaned_data['file']
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(StringIO(decoded_file))
                
                if not reader.fieldnames:
                    raise ValueError("El archivo CSV está vacío")
                
                # Validar columnas requeridas
                required_fields = {
                    'identifier', 'species', 'breed', 
                    'birth_date', 'birth_weight', 'health_status'
                }
                missing_fields = required_fields - set(reader.fieldnames)
                if missing_fields:
                    messages.error(
                        request, 
                        f"Columnas faltantes: {', '.join(missing_fields)}"
                    )
                    return render(request, 'carga_bulk.html', {'form': form})
                
                errores = []
                creados = 0
                
                for idx, row in enumerate(reader, 1):
                    try:
                        # Obtener o crear raza y zona
                        breed = get_or_create_breed(row['breed'])
                        pasture = get_or_create_pasture_zone(
                            row.get('pasture_zone', 'Default')
                        )
                        
                        # Crear animal
                        animal = Animal.objects.create(
                            identifier=row['identifier'].strip(),
                            species=row['species'].strip(),
                            breed=breed,
                            birth_date=row['birth_date'],
                            birth_weight=float(row['birth_weight']),
                            health_status=row['health_status'].strip(),
                            pasture_zone=pasture,
                            is_for_sale=row.get('is_for_sale', 'false').lower() == 'true',
                        )
                        creados += 1
                        logger.info(f"Animal creado: {animal.identifier}")
                        
                    except Exception as e:
                        error_msg = f"Fila {idx} ({row.get('identifier', 'sin ID')}): {str(e)}"
                        errores.append(error_msg)
                        logger.error(error_msg)
                
                # Mostrar resultados
                if creados > 0:
                    messages.success(request, f"✓ {creados} animal(es) importado(s) exitosamente")
                
                if errores:
                    messages.warning(
                        request, 
                        f"⚠ {len(errores)} fila(s) con error. Ver detalles abajo."
                    )
                    return render(request, 'carga_bulk.html', {
                        'form': form,
                        'errores': errores,
                        'creados': creados
                    })
                
                return redirect('admin_animales')
                
            except Exception as e:
                logger.error(f"Error procesando archivo CSV: {str(e)}")
                messages.error(request, f"Error procesando archivo: {str(e)}")
    else:
        form = BulkAnimalImportForm()
    
    return render(request, 'carga_bulk.html', {'form': form})
```

---

## ✅ Checklist de Implementación

```
Seguridad (P0)
[ ] Mover SECRET_KEY a .env
[ ] Cambiar DEBUG a False en producción
[ ] Crear .env.example

Validación (P1)
[ ] Crear ganaderia/forms.py con todos los formularios
[ ] Refactorizar create_animal para usar AnimalForm
[ ] Refactorizar update_animal para usar AnimalForm
[ ] Refactorizar add_weight_record para usar WeightRecordForm
[ ] Refactorizar carga_bulk_animales para usar BulkAnimalImportForm

Código Limpio (P1)
[ ] Eliminar imports duplicados en views.py
[ ] Crear ganaderia/utils_models.py
[ ] Eliminar print() de debug (línea 93)
[ ] Agregar docstrings a funciones principales

Logging (P2)
[ ] Crear ganaderia/logging_config.py
[ ] Agregar logging a vistas críticas
[ ] Crear directorio logs/

Testing (P2)
[ ] Crear ganaderia/tests/
[ ] Crear test_models.py
[ ] Crear test_views.py
[ ] Ejecutar: python manage.py test ganaderia

Documentación (P2)
[ ] Agregar docstrings a Animal, Breed, WeightRecord
[ ] Agregar docstrings a views principales
[ ] Actualizar README con instrucciones de setup
```

---

Implementar estas mejoras en el orden propuesto maximizará el impacto en calidad y seguridad del proyecto.
