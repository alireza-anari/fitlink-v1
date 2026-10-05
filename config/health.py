from django.db import DatabaseError, connection


def database_available() -> bool:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return cursor.fetchone() == (1,)
    except DatabaseError:
        return False
