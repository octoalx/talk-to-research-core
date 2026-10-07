"""Минимальный веб-интерфейс (веха M9). Пока только проверка, что сервер жив."""

from fastapi import FastAPI

from core import __version__

app = FastAPI(title="talk-to-research-core", version=__version__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}
