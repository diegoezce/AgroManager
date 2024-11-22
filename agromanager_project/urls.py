"""
URL configuration for AgroManager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
        2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path
from ganaderia.views import (input_growth_data, predict_growth, main_view, mapeo, cargar_geojson_view,
                             update_animal, admin_animales, create_animal, delete_animal, admin_campos, delete_campo,
                             settings_breeds, settings_pasture, settings_view, help_view, create_breed, delete_breed, 
                             add_weight_record, update_breed, dashboard_view, view_campo)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('predict/', predict_growth, name='predict_growth'),
    path('input/', input_growth_data, name='input_growth_data'),
    path('main/', dashboard_view, name='main'),
    # CONFIGURACION
    path('settings/', settings_view, name='settings'),
    path('mapeo/', mapeo, name='mapeo'),
    path('help/', help_view, name='help'),
    path('cargar_geojson_view/', cargar_geojson_view, name='cargar_geojson'),
    # ANIMALES
    path('admin_animales/', admin_animales, name='admin_animales'),
    path('update_animal/<int:animal_id>/', update_animal, name='update_animal'),
    path('delete_animal/<int:animal_id>/', delete_animal, name='delete_animal'),
    path('create_animal', create_animal, name='create_animal'),
    path('add_weight_record/<int:animal_id>/', add_weight_record, name='add_weight_record'),
    # CAMPOS
    path('admin_campos/', admin_campos, name='admin_campos'),
    path('delete_campo/<int:campo_id>/', delete_campo, name='delete_campo'),
    path('settings_breeds/', settings_breeds, name='settings_breeds'),
    path('settings_pasture/', settings_pasture, name='settings_pasture'),
    path('view_campo/<int:campo_id>/', view_campo, name='view_campo'),
    # RAZAS
    path('create_breed/', create_breed, name='create_breed'),
    path('delete_breed/<int:breed_id>/', delete_breed, name='delete_breed'),
    path('update_breed/<int:breed_id>/', update_breed, name='update_breed'),

]