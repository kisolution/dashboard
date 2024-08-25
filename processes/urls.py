from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('income/', views.display_income, name='display_income'),
    path('income/process/', views.process_income, name='process-income'),
    path('expense/', views.display_expense, name='display_expense'),
    path('fet_income_data/',views.fetch_income_data, name = 'fetch_income_data'),
    path('process-income/', views.process_income, name='process_income'),
    path('fet_expense_data/',views.fetch_expense_data, name = 'fetch_expense_data'),
    path('process-expense/', views.process_expense, name='process_expense'),
    #path('expense/process/', views.process_expense, name='process-expense'),
    #path('income_processing_status/', views.income_processing_status, name='income_processing_status'),
    #path('expense_processing_status/', views.expense_processing_status, name='expense_processing_status'),
    #path('check_task_status/<str:task_id>/', views.check_task_status, name='check_task_status'),
    

    #path('income-status/', views.income_status, name='income_status'),
    path('history', views.show_history, name = 'history'),
    re_path(r'download-history/(?P<s3_key>.+)$', views.download_history, name='download-history'),
]
