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
from django.contrib import admin
from django.urls import path
from ganaderia.views import (input_growth_data, predict_growth, main_view, mapeo, cargar_geojson_view,
                             update_animal, admin_animales, create_animal, delete_animal, admin_campos)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('predict/', predict_growth, name='predict_growth'),
    path('input/', input_growth_data, name='input_growth_data'),
    path('main/', main_view, name='main'),
    path('admin_animales/', admin_animales, name='admin_animales'),
    path('create_animal', create_animal, name='create_animal'),
    path('settings/', main_view, name='settings'),
    path('mapeo/', mapeo, name='mapeo'),
    path('help/', main_view, name='help'),
    path('cargar_geojson_view/', cargar_geojson_view, name='cargar_geojson'),
    path('update_animal/<int:animal_id>/', update_animal, name='update_animal'),
    path('delete_animal/<int:animal_id>/', delete_animal, name='delete_animal'),
    path('admin_campos/', admin_campos, name='admin_campos'),

]