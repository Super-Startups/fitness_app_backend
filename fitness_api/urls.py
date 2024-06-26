from django.http import JsonResponse
from django.urls import path

from fitness_api.views import test_response

urlpatterns = [
    path('test/', test_response),
]
