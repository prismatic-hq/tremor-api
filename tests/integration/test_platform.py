from fastapi.testclient import TestClient
from sqlalchemy import Engine, text


def test_healthz_is_ok(client: TestClient) -> None:
    assert client.get("/healthz").json() == {"status": "ok"}


def test_readyz_is_ok_when_database_reachable(client: TestClient) -> None:
    response = client.get("/readyz")

    assert response.status_code == 200


def test_metrics_exposes_prometheus_text(client: TestClient) -> None:
    client.get("/alerts")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text


def test_migrations_live_in_service_schema(engine: Engine) -> None:
    with engine.connect() as connection:
        tables = connection.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'tremor'")
        ).scalars()

        assert {"alerts", "alembic_version"} <= set(tables)
