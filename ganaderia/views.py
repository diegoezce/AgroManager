"""
Views for animal management application.
Handles animal CRUD, weight tracking, breeds, pasture zones, and geospatial mapping.
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
from .models import Animal, Breed, PastureZone, Campo, WeightRecord
from .utils import cargar_datos_geoespaciales

logger = logging.getLogger(__name__)

# Load ML model
try:
    model_path = 'ml_models/modelo_crecimiento.pkl'
    pipeline = joblib.load(model_path)
except FileNotFoundError:
    logger.error(f"ML model not found at {model_path}")
    pipeline = None


def predict_growth(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        birth_date = request.POST['birth_date']
        breed = request.POST['breed']
        pasture_zone = request.POST['pasture_zone']
        health_status = request.POST['health_status']
        date = request.POST['date']
        if (request.POST['weight']):
            weight = float(request.POST['weight'])
        else:
            weight = 0

        # Crear un diccionario con los datos
        data = {
            'birth_date': birth_date,
            'breed': breed,
            'pasture_zone': pasture_zone,
            'health_status': health_status,
            'date': date,
            'weight': weight,
        }

        # Transformar los datos de entrada en un DataFrame para predecir
        input_df = pd.DataFrame([data])

        # Realizar la predicción usando el pipeline
        prediction = pipeline.predict(input_df)

        return render(request, 'prediction_result.html', {'prediction': prediction, 'data': data})


def input_growth_data(request):
    razas = ['Hereford', 'Brahman', 'Angus', 'Charolais']
    return render(request, 'prediction_input.html', {'razas': razas})


def main_view(request):

    return render(request, 'main.html')


def admin_animales(request):
    """List all animals with filters and pagination."""
    animal_filter = AnimalFilter(request.GET, queryset=Animal.objects.all())
    pasture_zones = PastureZone.objects.all()
    breeds_list = Breed.objects.all()

    paginator = Paginator(animal_filter.qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'selected_breed': request.GET.get('breed', ''),
        'selected_specie': request.GET.get('species', ''),
        'selected_pasture_zones': request.GET.get('pasture_zone', ''),
        'selected_health': request.GET.get('health_status', ''),
        'animals_list': page_obj,
        'breeds_list': breeds_list,
        'page_obj': page_obj,
        'filter': animal_filter,
        'pasturezones': pasture_zones,
    }
    return render(request, 'admin_animales.html', context)


def carga_bulk_animales(request):
    """Import multiple animals from CSV file with validation."""
    if request.method == 'POST':
        form = BulkAnimalImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = form.cleaned_data['file']
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(StringIO(decoded_file))

                if not reader.fieldnames:
                    messages.error(request, "CSV file is empty")
                    return render(request, 'carga_bulk.html', {'form': form})

                # Validate required columns
                required_fields = {
                    'identifier', 'species', 'breed',
                    'birth_date', 'birth_weight', 'health_status'
                }
                missing_fields = required_fields - set(reader.fieldnames or [])
                if missing_fields:
                    messages.error(
                        request,
                        f"Missing columns: {', '.join(missing_fields)}"
                    )
                    return render(request, 'carga_bulk.html', {'form': form})

                errores = []
                creados = 0

                for idx, row in enumerate(reader, 1):
                    try:
                        breed, _ = Breed.objects.get_or_create(name=row['breed'].strip())
                        pasture, _ = PastureZone.objects.get_or_create(
                            name=row.get('pasture_zone', 'Default').strip()
                        )

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
                        logger.info(f"Animal created from CSV: {animal.identifier}")

                    except Exception as e:
                        error_msg = f"Row {idx} ({row.get('identifier', 'no-id')}): {str(e)}"
                        errores.append(error_msg)
                        logger.error(error_msg)

                if creados > 0:
                    messages.success(request, f"✓ {creados} animal(s) imported successfully")

                if errores:
                    messages.warning(request, f"⚠ {len(errores)} row(s) with errors")
                    return render(request, 'carga_bulk.html', {
                        'form': form,
                        'errores': errores,
                        'creados': creados
                    })

                return redirect('admin_animales')

            except Exception as e:
                logger.error(f"Error processing CSV file: {str(e)}")
                messages.error(request, f"Error processing file: {str(e)}")
                return render(request, 'carga_bulk.html', {'form': form})
    else:
        form = BulkAnimalImportForm()

    return render(request, 'carga_bulk.html', {'form': form})


def mapeo(request):
    return render(request, 'mapeo.html')


def cargar_geojson_view(request):
    if request.method == 'POST':
        # Obtener el archivo (opcional) y la geometría del campo
        archivo_geojson = request.FILES.get('archivo')
        geometria_json = request.POST.get('geometria')
        name = request.POST.get('name')

        if geometria_json:
            geometria = json.loads(geometria_json)  # Convertir el string JSON a un objeto
            # Aquí puedes procesar la geometría como desees
            # Por ejemplo, puedes guardarla en tu base de datos

            cargar_datos_geoespaciales(geometria, archivo_geojson, name)  # Asegúrate de que esta función pueda manejar geometría

            return JsonResponse({'message': 'Datos cargados correctamente.'})

        return JsonResponse({'error': 'No se proporcionó ninguna geometría.'}, status=400)

    # Si no es una solicitud POST, simplemente renderiza el formulario
    return render(request, 'cargar_geojson.html')


def view_campo(request, campo_id):
      # Obtener el campo por ID
    campo = get_object_or_404(Campo, id=campo_id)
    # Convertir la geometría WKT a GeoJSON
    geojson = {
        "type": "Feature",
        "properties": {
            "name": campo.name,
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [[float(coord.split()[0]), float(coord.split()[1])] for coord in campo.geometria.replace("POLYGON ((", "").replace("))", "").split(", ")]
            ]
        }
    }
    # Renderizar la plantilla y pasar la geometría como contexto
    return render(request, 'view_campo.html', {'campo_geojson': geojson, 'campo': campo})


def create_animal(request):
    """Create a new animal with validated form."""
    if request.method == 'POST':
        form = AnimalForm(request.POST)
        if form.is_valid():
            animal = form.save()
            messages.success(request, f'Animal "{animal.identifier}" created successfully')
            logger.info(f"Animal created: {animal.identifier} by user {request.user}")
            return redirect('admin_animales')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            logger.warning(f"Animal form validation failed: {form.errors}")
    else:
        form = AnimalForm()

    return render(request, 'animal_form.html', {'form': form, 'title': 'Create Animal'})


def update_animal(request, animal_id):
    if request.method == 'POST':
        field = request.POST.get('field')
        value = request.POST.get('value')

        try:
            animal = Animal.objects.get(id=animal_id)
            # Convierte el valor a booleano si es para el campo `is_for_sale`
            if field == 'is_for_sale':
                setattr(animal, field, value == 'True')
            else:
                setattr(animal, field, value)
            animal.save()
            return JsonResponse({'status': 'success'})
        except Animal.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Animal no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def delete_animal(request, animal_id):
    if request.method == 'DELETE':

        try:
            animal = Animal.objects.get(id=animal_id)
            animal.delete()

            messages.success(request, 'Animal eliminado correctamente.')
            return JsonResponse({'success': True, 'message': 'Registro eliminado exitosamente.'})

        except Animal.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Registro no encontrado.'}, status=404)
        

def add_weight_record(request, animal_id):
    """Add a weight record for an animal with validation."""
    animal = get_object_or_404(Animal, id=animal_id)

    if request.method == 'POST':
        form = WeightRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.animal = animal
            record.save()
            messages.success(request, f'Weight recorded: {record.weight}kg on {record.date_recorded}')
            logger.info(f"Weight record added for {animal.identifier}: {record.weight}kg")
            return redirect('admin_animales')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = WeightRecordForm()

    return render(request, 'weight_record_form.html', {
        'form': form,
        'animal': animal,
        'title': f'Add Weight Record for {animal.identifier}'
    })


def admin_campos(request):
    campos_list = Campo.objects.all()
    return render(request, 'admin_campos.html', {'campos_list': campos_list})


def delete_campo(request, campo_id):
    if request.method == 'DELETE':

        try:

            campo = Campo.objects.get(id=campo_id)
            campo.delete()

            messages.success(request, 'Campo eliminado correctamente.')
            return JsonResponse({'success': True, 'message': 'Registro eliminado exitosamente.'})

        except Animal.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Registro no encontrado.'}, status=404)


def settings_view(request):

    return render(request, 'settings.html')


def settings_breeds(request):
    breed_list = Breed.objects.all()
    return render(request, 'settings_breeds.html',{'breed_list': breed_list})


def create_breed(request):
    """Create a new breed with validation."""
    if request.method == 'POST':
        form = BreedForm(request.POST)
        if form.is_valid():
            breed = form.save()
            messages.success(request, f'Breed "{breed.name}" created successfully')
            logger.info(f"Breed created: {breed.name}")
            return redirect('settings_breeds')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = BreedForm()

    return render(request, 'breed_form.html', {'form': form, 'title': 'Create Breed'})


def delete_breed(request, breed_id):
    if request.method == 'DELETE':

        try:

            breed = Breed.objects.get(id=breed_id)
            breed.delete()

            messages.success(request, 'Raza eliminado correctamente.')
            return JsonResponse({'success': True, 'message': 'Registro eliminado exitosamente.'})

        except Breed.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Registro no encontrado.'}, status=404)


def update_breed(request, breed_id):
    """Update a breed field via AJAX."""
    breed = get_object_or_404(Breed, id=breed_id)

    if request.method == 'POST':
        field = request.POST.get('field')
        value = request.POST.get('value')

        try:
            setattr(breed, field, value)
            breed.full_clean()  # Validate before saving
            breed.save()
            logger.info(f"Breed updated: {breed.name}")
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Error updating breed {breed_id}: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)


def help_view(request):
    return render(request, 'help.html')


def settings_pasture(request):

    return render(request, 'settings_pasture.html')


def dashboard_view(request):
    # Obtén el identifier de la vaca del parámetro de solicitud (GET o POST, según cómo lo envíes)
    identifier = request.GET.get('identifier', None)

    weight_data = []

    # Si hay un identifier válido, obtén los datos de peso para esa vaca
    if identifier:
        animal = get_object_or_404(Animal, identifier=identifier)
        weight_records = WeightRecord.objects.filter(animal=animal).order_by('date_recorded')

        # Llenar weight_data con los registros de peso para esta vaca específica
        weight_data = [
            {
                'date': record.date_recorded.strftime('%Y-%m-%d'),
                'weight': record.weight
                
            }
            for record in weight_records
        ]
       
   # Total de animales
    total_animals = Animal.objects.count()

    # Animales para la venta
    animals_for_sale = Animal.objects.filter(is_for_sale=True).count()

    # Nacidos este mes
    born_this_month = Animal.objects.filter(birth_date__month=now().month).count()

    # Promedio de peso al nacer
    average_birth_weight = Animal.objects.aggregate(Avg('birth_weight'))['birth_weight__avg']

    # Promedio de peso actual (usando weight_records)
    average_current_weight = Animal.objects.annotate(
        latest_weight=Subquery(WeightRecord.objects.filter(animal=OuterRef('pk')).order_by('-date_recorded').values('weight')[:1])
    ).aggregate(Avg('latest_weight'))['latest_weight__avg']

    # Porcentaje de animales saludables
    total_health_status = Animal.objects.filter(health_status="Saludable").count()
    healthy_percentage = (total_health_status / total_animals) * 100 if total_animals > 0 else 0

    # Tasa de mortalidad
    mortality_rate = Animal.objects.filter(health_status="Muerto").count()
    mortality_rate_percentage = (mortality_rate / total_animals) * 100 if total_animals > 0 else 0

    context = {
       
    }

    try:
    # Enviar los datos de peso y todos los identifiers de las vacas al template
        context = {
            'weight_data_json': json.dumps(weight_data),  # Para el gráfico
            'animal_selected': animal,
            'animals': Animal.objects.all(),              # Para el dropdown
            'selected_identifier': identifier,             # Para mostrar el ID seleccionado
            'total_animals': total_animals,
            'animals_for_sale': animals_for_sale,
            'born_this_month': born_this_month,
            'average_birth_weight': average_birth_weight,
            'average_current_weight': average_current_weight,
            'healthy_percentage': healthy_percentage,
            'mortality_rate': mortality_rate_percentage,
        }
    except:
        context = {
            'weight_data_json': json.dumps(weight_data),  # Para el gráfico         
            'animals': Animal.objects.all(),              # Para el dropdown
            'selected_identifier': identifier,             # Para mostrar el ID seleccionado
            'total_animals': total_animals,
            'animals_for_sale': animals_for_sale,
            'born_this_month': born_this_month,
            'average_birth_weight': average_birth_weight,
            'average_current_weight': average_current_weight,
            'healthy_percentage': healthy_percentage,
            'mortality_rate': mortality_rate_percentage,
        }
    return render(request, 'main.html', context)

   