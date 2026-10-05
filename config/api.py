from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class StatusView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({"service": "fitlink", "api_version": "v1", "status": "ok"})
