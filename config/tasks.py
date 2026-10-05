from .celery import app


@app.task(name="config.tasks.infrastructure_probe")
def infrastructure_probe() -> dict[str, str]:
    return {"status": "ok"}
