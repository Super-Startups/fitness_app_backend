from django.http import JsonResponse
from django.urls import path

from fitness_api.views import get_material, ask_question

urlpatterns = [
    path('get-material/', get_material),
    path('ask-question/', ask_question),
]
