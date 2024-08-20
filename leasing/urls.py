from django.urls import include, path
from . import views
urlpatterns = [
    path('getting-value', views.process_leasing, name = 'leasing-process')
]