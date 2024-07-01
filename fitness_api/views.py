from django.http import JsonResponse
import json


def test_response(request):
    request_json = json.loads(request.body)
    json_response = ApiResponse().__dict__
    return JsonResponse(json_response)


class ApiRequest:
    coach_id = None


class ApiResponse:
    message = 'Hello, World!'
