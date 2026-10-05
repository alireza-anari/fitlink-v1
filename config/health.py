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
