# soccer_app/urls.py
from django.urls import path
from . import views

app_name = 'soccer_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('load-data/', views.load_data, name='load_data'),
    path('api/standings/', views.api_standings, name='api_standings'),
]