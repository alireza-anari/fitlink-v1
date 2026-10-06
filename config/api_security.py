from django.http import JsonResponse


def csrf_failure(request, reason=""):
    response = JsonResponse({"status": "denied"}, status=403)
    response["Cache-Control"] = "no-store"
    return response
