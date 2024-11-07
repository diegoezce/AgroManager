import json
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render
import joblib
import pandas as pd
from django.views.decorators.csrf import csrf_exempt

from . import utils
from .models import Animal, Breed, PastureZone, Campo
from django.http import JsonResponse

from .utils import cargar_datos_geoespaciales

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
    animals_list = Animal.objects.all()
    breeds_list = Breed.objects.all()
    return render(request, 'admin_animales.html', {'animals_list': animals_list, 'breeds_list': breeds_list})


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
            animal.weight = request.POST.get('weight')
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

def help_view(request):
    return render(request, 'help.html')

def settings_pasture(request):

    return render(request, 'settings_pasture.html')