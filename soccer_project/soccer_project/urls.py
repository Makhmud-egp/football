# project_name/urls.py (your main project folder)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('soccer_app.urls')),  # This line includes your app's URLs
]