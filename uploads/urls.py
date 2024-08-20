from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.home_upload_view, name='home'),
    path('download_sample/<str:upload_type>/', views.download_sample, name='download_sample')
    

]