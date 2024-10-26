import random
import pandas as pd
import datetime
import numpy as np


def calcular_fechas(edad_meses):
    fecha_actual = datetime.datetime.now()
    anios, meses = divmod(edad_meses, 12)
    mes_nacimiento = (fecha_actual.month - meses) if (fecha_actual.month - meses) > 0 else (
                12 + (fecha_actual.month - meses))
    anio_nacimiento = fecha_actual.year - anios - (1 if mes_nacimiento > 12 else 0)
    fecha_nacimiento = fecha_actual.replace(year=anio_nacimiento, month=mes_nacimiento)

    fecha_edad = fecha_nacimiento + datetime.timedelta(days=edad_meses * 30)

    return fecha_nacimiento.strftime('%Y-%m-%d'), fecha_edad.strftime('%Y-%m-%d')


def calcular_peso(edad_meses, params):
    peso_inicial = params['peso_inicial']
    peso_maximo = params['peso_maximo']
    edad_inflexion = params['edad_inflexion']  # Edad en meses donde comienza la desaceleración

    # Modelo de crecimiento sigmoide
    # Crecimiento acelerado inicialmente y desaceleración luego
    k = 1.0  # Tasa de crecimiento, puedes ajustarla
    peso_actual = peso_maximo / (1 + np.exp(-k * (edad_meses - edad_inflexion)))

    # Asegurarse de no exceder el peso máximo
    if peso_actual > peso_maximo:
        peso_actual = peso_maximo

    return round(peso_actual)


# Parámetros para cada raza
razas = {
    'Charolais': {
        'peso_inicial': 250,
        'peso_maximo': 600,
        'edad_inflexion': 8  # Meses
    },
    'Angus': {
        'peso_inicial': 230,
        'peso_maximo': 550,
        'edad_inflexion': 7  # Meses
    },
    'Hereford': {
        'peso_inicial': 240,
        'peso_maximo': 570,
        'edad_inflexion': 6  # Meses
    }
}

# Crear DataFrame
data = []

# Definir el número total de registros que deseas
num_registros = 300

for _ in range(num_registros):  # Generar 'num_registros' datos
    edad = random.randint(15, 24)  # Seleccionar una edad aleatoria entre 15 y 24 meses
    raza = random.choice(list(razas.keys()))  # Seleccionar raza aleatoriamente
    params = razas[raza]  # Obtener parámetros de la raza

    # Calcular el peso en función de la edad
    peso_actual = calcular_peso(edad, params)

    # Calcular el porcentaje de grasa
    if peso_actual < 400:  # Ejemplo para categorías de menor peso
        porcentaje_grasa = 16
    else:
        porcentaje_grasa = 20

    pastura = 'Norte'
    # Añadir datos a la lista
    fecha_nac, fecha_edad = calcular_fechas(edad)
    data.append([fecha_nac, raza, pastura, 'Bueno', fecha_edad, peso_actual])

# Convertir a DataFrame
df = pd.DataFrame(data, columns=['birth_date', 'breed', 'pasture_zone', 'health_status', 'date', 'weight'])

# Exportar el DataFrame a CSV
df.to_csv('datos_ganado_actualizado.csv', index=False)

# Mostrar el DataFrame
print(df)