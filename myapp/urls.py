"""
URL configuration for BearingCode project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('create/', views.create_entry, name='create_entry'),
    path('admin/', views.admin_view, name='admin_view'),
    path('crbrk/', views.create_breaks, name='create_breaks'),
    path('dbf/', views.download_break_file, name='download_break_file'),
    path('del/', views.delete_all_data, name='delete_all_data'),
    path('dwn/', views.download_all_data, name='download_all_data'),
    path('crt/', views.create_new_group, name='create_new_group'),    
]