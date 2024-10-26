from django.shortcuts import render
import joblib
import pandas as pd
from numpy.random import weibull

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