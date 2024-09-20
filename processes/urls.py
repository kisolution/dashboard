from django.urls import path, re_path
from . import views

urlpatterns = [
    path('display-income/', views.display_income, name='display_income'),
    path('display-expense/', views.display_expense, name='display_expense'),
    path('initiate-income-process/', views.initiate_income_process, name='initiate_income_process'),
    path('initiate-expense-process/', views.initiate_expense_process, name='initiate_expense_process'),
    path('history', views.show_history, name = 'history'),
    re_path(r'download-history/(?P<s3_key>.+)$', views.download_history, name='download-history'),
]
