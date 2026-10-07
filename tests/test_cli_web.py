from fastapi.testclient import TestClient

from cli.main import main
from web.app import app


def test_cli_check(capsys) -> None:  # type: ignore[no-untyped-def]
    assert main(["check"]) == 0
    assert "sqlite-vec" in capsys.readouterr().out


def test_health() -> None:
    assert TestClient(app).get("/health").json()["status"] == "ok"
