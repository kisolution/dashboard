from django.urls import path, include
from . import views

urlpatterns = [
    path('income/', views.display_income, name='display_income'),
    path('income/process/', views.process_income, name='process-income'),
    path('expense/', views.display_expense, name='display_expense'),
    path('expense/process/', views.process_expense, name='process-expense'),
    #path('income/',views.income_process, name = 'process-income'),
    #path('processed-income/', views.display_processed_income, name='display_processed_income'),
    #path('expense/',views.expense_process, name = 'process-expense'),
    #path('processed-expense/', views.display_processed_expense, name='display_processed_expense'),
]

