from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def redirect_to_dashboard(request):
    return redirect('/dashboard/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_dashboard),
    path('', include('loans.urls')),
    path('django-rq/', include('django_rq.urls')),
]