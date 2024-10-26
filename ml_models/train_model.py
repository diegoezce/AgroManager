import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
import joblib

# Cargar el dataset
data = pd.read_csv('datos_ganado_actualizado.csv')

# Definir las características y el objetivo
features = data[['birth_date', 'breed', 'pasture_zone', 'health_status', 'date']]
target = data['weight']  # Vamos a predecir el peso

# Preprocesamiento: definir las transformaciones
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['birth_date', 'breed', 'pasture_zone', 'health_status', 'date']),
    ]
)

# Crear el modelo de pipeline
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', RandomForestRegressor())
])

# Dividir el conjunto de datos en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# Entrenar el modelo
pipeline.fit(X_train, y_train)

# Guardar el modelo entrenado en la carpeta `ml_models`
joblib.dump(pipeline, 'modelo_crecimiento.pkl')