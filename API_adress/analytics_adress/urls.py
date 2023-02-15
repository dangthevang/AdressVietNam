from django.urls import path
from . import views

urlpatterns = [
    path('', views.view, name='view'),
    path('adress/', views.getAPI, name='API')]