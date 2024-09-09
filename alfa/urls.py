from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('uploads.urls')),
    path('accounts/', include('users.urls')),  # This should come before django.contrib.auth.urls
    path('accounts/', include('django.contrib.auth.urls')),
    path('processes/', include('processes.urls')),
    path('leasing/', include('leasing.urls')),
    path('prediction/', include('prediction.urls')),
    path('policy/',include('policy.urls') ),
    path('policy-process/',include('polcyprocess.urls') ),
]
