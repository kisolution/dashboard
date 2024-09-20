from django.urls import path, include
from . import views

urlpatterns = [
    path('display-income-prediction', views.display_income_prediction, name = 'display_income_prediction'),
    path('intiate-income-prediction', views.initiate_income_prediction, name = 'initiate-income-prediction'),
    path('display-expense-prediction', views.display_expense_prediction, name = 'display_expense_prediction'),
    path('intiate-expense-prediction', views.initiate_expense_prediction, name = 'initiate-expense-prediction'),
]