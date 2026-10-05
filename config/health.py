from django.db import DatabaseError, connection


def database_available() -> bool:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return cursor.fetchone() == (1,)
    except DatabaseError:
        return False


from django.conf import settings
from redis import Redis
from redis.exceptions import RedisError


def redis_available() -> bool:
    try:
        with Redis.from_url(
            settings.REDIS_URL, socket_connect_timeout=2, socket_timeout=2
        ) as client:
            return bool(client.ping())
    except (RedisError, ValueError):
        return False


from django.http import JsonResponse


def liveness(request):
    response = JsonResponse({"status": "ok"})
    response["Cache-Control"] = "no-store"
    return response


def readiness(request):
    ready = database_available() and redis_available()
    response = JsonResponse(
        {"status": "ok" if ready else "unavailable"}, status=200 if ready else 503
    )
    response["Cache-Control"] = "no-store"
    return response
