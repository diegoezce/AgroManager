import json

from django.shortcuts import render
import joblib
import pandas as pd
from django.views.decorators.csrf import csrf_exempt

from . import utils
from .models import Animal
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
    animals_list = Animal.objects.all()

    return render(request, 'main.html', {'animals_list': animals_list})


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