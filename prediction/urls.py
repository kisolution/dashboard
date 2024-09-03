from django.urls import path, include
from . import views

urlpatterns = [
    path('income-prediction', views.income_prediction, name = 'income-prediction')
]