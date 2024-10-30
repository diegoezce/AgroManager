import geopandas as gpd
from shapely import wkt  # Importa WKT para convertir geometrías
from .models import Campo
from shapely.geometry import shape  # Para convertir de GeoJSON a geometría de Shapely


def cargar_datos_geoespaciales(geometria_json, archivo_geojson=None, name='Nombre del Campo'):
    # Convertir la geometría de GeoJSON a Shapely
    geometria = shape(geometria_json['geometry'])

    # Crear un nuevo objeto Campo y guardar en la base de datos
    campo = Campo(
        name= name,  # Ajusta según tus necesidades
        geometria=geometria.wkt  # Guarda como WKT
    )
    campo.save()

    if archivo_geojson:
        # Procesar el archivo GeoJSON aquí, si es necesario
        gdf = gpd.read_file(archivo_geojson)
        # Guarda en la base de datos como en el ejemplo anterior