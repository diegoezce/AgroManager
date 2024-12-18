import json
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
import joblib
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.timezone import now
from django.db.models import Count, Avg, F
from . import utils
from django.db.models import Subquery, OuterRef

from .models import Animal, Breed, PastureZone, Campo, WeightRecord
from django.http import JsonResponse
from django.core.serializers import serialize
from .utils import cargar_datos_geoespaciales
from django.http import JsonResponse
from .models import Campo
from django.shortcuts import render, get_object_or_404
from .models import Campo
from django.http import HttpResponseRedirect
from django.urls import reverse
import csv
from django.core.paginator import Paginator
from .models import Animal
from .filters import AnimalFilter

# Cargar el modelo (esto se puede hacer al inicio o con lazy loading si prefieres)
model_path = 'ml_models/modelo_crecimiento.pkl'
pipeline = joblib.load(model_path)  # Asegúrate de usar la ruta correcta


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
    animals = Animal.objects.all()
    animal_filter = AnimalFilter(request.GET, queryset=Animal.objects.all())
    
    #retain the values of the filters
    breedFilter = request.GET.get('breed', '')
    healthFilter = request.GET.get('health_status','')
    pasture_zonesFilter = request.GET.get('pasture_zone','')
    speciesFilter = request.GET.get('species','')


    pasture_zones = PastureZone.objects.all()

    paginator = Paginator(animal_filter.qs, 10)  # Aplica el paginador al queryset filtrado
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    breeds_list = Breed.objects.all()
    print(request.GET)
    return render(request, 'admin_animales.html',
                   {'selected_breed': breedFilter,
                    'selected_specie': speciesFilter,
                    'selected_pasture_zones': pasture_zonesFilter,
                    'selected_health': healthFilter,
                     'animals_list': page_obj,
                       'breeds_list': breeds_list,
                         'page_obj': page_obj,
                           'filter': animal_filter,
                             'pasturezones': pasture_zones})


def carga_bulk_animales(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        errores = []
        for row in reader:
            try:
                # Ejemplo de validación y creación
                breed = Breed.objects.get(name=row['breed'])  # Validar que la raza exista
                pasture_zone = PastureZone.objects.get(name=row['pasture_zone'])  # Validar que la zona exista

                Animal.objects.create(
                    identifier=row['identifier'],
                    species=row['species'],
                    breed=breed,
                    birth_date=row['birth_date'],
                    birth_weight=float(row['birth_weight']),
                    health_status=row['health_status'],
                    pasture_zone=pasture_zone,
                    is_for_sale=row.get('is_for_sale', '').lower() == 'true',
                )
            except Exception as e:
                errores.append(f"Error en la fila {row['identifier']}: {str(e)}")

        if errores:
            return render(request, 'carga_bulk.html', {'errores': errores})

        return HttpResponseRedirect(reverse('admin_animales'))  # Redirige después de cargar
    return render(request, 'carga_bulk.html')


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
    if request.method == 'POST':
        # Suponiendo que 'animal' es el objeto al que quieres asignar los valores.
        try:
            animal = Animal()
            animal.identifier = request.POST.get('identifier')
            animal.species = request.POST.get('species')

            breed_name = request.POST.get('breed')
            breed, created = Breed.objects.get_or_create(name=breed_name)

            pasture_name = request.POST.get('pasture_zone')
            pasture, pasture_created = PastureZone.objects.get_or_create(name=pasture_name)

            if request.POST.get('is_for_sale') == '':
                sale = False
            else:
                sale = True

            animal.breed = breed
            animal.birth_date = request.POST.get('birth_date')
            animal.birth_weight = request.POST.get('birth_weight')
            animal.health_status = request.POST.get('health_status')
            animal.pasture_zone = pasture
            animal.is_for_sale = sale
            animal.save()
            messages.success(request, 'Datos guardados exitosamente.')
            return redirect('admin_animales')

        except Exception as e:

            messages.error(request, f'Error al guardar los datos: {e}')

            return redirect('admin_animales')  # Redirige a la misma página en caso de error


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
    if request.method == 'POST':
        try:
            
            animal = Animal.objects.get(id=animal_id)
            p_weight = request.POST.get('weight')
            print(f" PESO {request.POST.get('weight')}")
            weight_date = request.POST.get('weight_date', timezone.now())
            
            print(f"animal: {animal_id}, peso: {p_weight}, fecha: {weight_date}" )

            new_weight_record = WeightRecord(animal=animal, weight=p_weight)
            new_weight_record.date_recorded = weight_date
            new_weight_record.save()

            messages.success(request, 'Peso agregado correctamente.')
            return JsonResponse({'success': True, 'message': 'Registro agregado exitosamente.'})

        except Animal.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Registro no encontrado.'}, status=404)


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
    if request.method == 'POST':
        try:
            breed = Breed()
            breed.name = request.POST.get('name')
            breed.description = request.POST.get('description')

            breed.save()
            messages.success(request, 'Datos guardados exitosamente.')
            return redirect('settings_breeds')

        except Exception as e:

            messages.error(request, f'Error al guardar los datos: {e}')

            return redirect('settings_breeds')  # Redirige a la misma página en caso de error


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
    if request.method == 'POST':
        field = request.POST.get('field')
        value = request.POST.get('value')

        try:
            breed = Breed.objects.get(id=breed_id)
            setattr(breed, field, value)
            print(f'dates: {breed} {breed.name} {breed.description} {breed_id}')
            breed.save()
            return JsonResponse({'status': 'success'})
        except Animal.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Animal no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


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

   