from django.http import JsonResponse


def test_response(request):
    print(request.body)
    return JsonResponse({'message': 'Hello, World!'})
