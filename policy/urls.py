from django.urls import path, include
from . import views
urlpatterns = [
    path('policy-upload',  views.policy_upload_view, name = 'policy-upload'),
    path('download_policy_sample/<str:upload_type>/', views.download_policy_sample, name='download_policy_sample')

]