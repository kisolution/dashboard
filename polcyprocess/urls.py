from django.urls import path, include
from . import views

urlpatterns = [
    path('process-policy', views.display_policy_income, name = 'display-policy'),
    path('initiate-process-policy', views.initiate_policy_process, name = 'process-policy')
]