import socket

from fastapi.testclient import TestClient
from sqlalchemy import Engine

from tests.steward_stub import StewardStub
from tremor_api.config import DatabaseSettings, StewardSettings
from tremor_api.main import create_app

CRITICAL_ALERT = {"station": "KIL-01", "severity": "critical", "magnitude": 5.1, "message": "Vent"}


def test_critical_alert_opens_high_priority_work_order(
    client: TestClient, steward: StewardStub
) -> None:
    response = client.post("/alerts", json=CRITICAL_ALERT)

    assert response.status_code == 201, response.text
    alert = response.json()
    assert alert["work_order_id"] == steward.work_order_id
    assert steward.requests == [
        (
            "/work-orders",
            {
                "site": "KIL-01",
                "title": "Inspect KIL-01: critical alert",
                "priority": "high",
                "source_alert_id": alert["id"],
            },
        )
    ]


def test_critical_alert_link_is_persisted(client: TestClient, steward: StewardStub) -> None:
    alert = client.post("/alerts", json=CRITICAL_ALERT).json()

    assert client.get(f"/alerts/{alert['id']}").json()["work_order_id"] == steward.work_order_id


def test_non_critical_alert_never_calls_steward(client: TestClient, steward: StewardStub) -> None:
    response = client.post("/alerts", json={**CRITICAL_ALERT, "severity": "warning"})

    assert response.status_code == 201
    assert response.json()["work_order_id"] is None
    assert steward.requests == []


def test_steward_error_returns_502_and_keeps_no_alert(
    client: TestClient, steward: StewardStub
) -> None:
    steward.status = 500

    response = client.post("/alerts", json=CRITICAL_ALERT)

    assert response.status_code == 502
    assert response.json()["detail"].startswith("steward-api unavailable: ")
    assert "500" in response.json()["detail"]
    assert client.get("/alerts").json() == []


def test_steward_timeout_returns_502_and_keeps_no_alert(
    client: TestClient, steward: StewardStub
) -> None:
    steward.delay_seconds = 1.0

    response = client.post("/alerts", json=CRITICAL_ALERT)

    assert response.status_code == 502
    assert "timed out" in response.json()["detail"]
    assert client.get("/alerts").json() == []


def test_unreachable_steward_returns_502(db_settings: DatabaseSettings, engine: Engine) -> None:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        closed_port = probe.getsockname()[1]
    settings = StewardSettings(url=f"http://127.0.0.1:{closed_port}", timeout_seconds=0.5)

    with TestClient(create_app(db_settings, settings)) as client:
        response = client.post("/alerts", json=CRITICAL_ALERT)

    assert response.status_code == 502
    assert response.json()["detail"].startswith("steward-api unavailable: ")
