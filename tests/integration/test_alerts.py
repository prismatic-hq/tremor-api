import uuid

from fastapi.testclient import TestClient

NEW_ALERT = {"station": "KIL-01", "severity": "warning", "magnitude": 3.2, "message": "Tilt spike"}


def create_alert(client: TestClient, **overrides: object) -> dict:
    response = client.post("/alerts", json={**NEW_ALERT, **overrides})
    assert response.status_code == 201, response.text
    return response.json()


def test_create_alert_returns_open_alert(client: TestClient) -> None:
    alert = create_alert(client)

    assert alert["station"] == "KIL-01"
    assert alert["status"] == "open"
    assert uuid.UUID(alert["id"])


def test_create_alert_rejects_unknown_severity(client: TestClient) -> None:
    response = client.post("/alerts", json={**NEW_ALERT, "severity": "apocalyptic"})

    assert response.status_code == 422


def test_list_alerts_returns_created_alerts(client: TestClient) -> None:
    first = create_alert(client)
    second = create_alert(client, station="KIL-02")

    response = client.get("/alerts")

    assert response.status_code == 200
    assert [a["id"] for a in response.json()] == [first["id"], second["id"]]


def test_get_alert_by_id(client: TestClient) -> None:
    alert = create_alert(client)

    response = client.get(f"/alerts/{alert['id']}")

    assert response.status_code == 200
    assert response.json() == alert


def test_get_missing_alert_returns_404(client: TestClient) -> None:
    response = client.get(f"/alerts/{uuid.uuid4()}")

    assert response.status_code == 404


def test_update_alert_changes_only_given_fields(client: TestClient) -> None:
    alert = create_alert(client)

    response = client.patch(f"/alerts/{alert['id']}", json={"status": "acknowledged"})

    assert response.status_code == 200
    assert response.json()["status"] == "acknowledged"
    assert response.json()["message"] == alert["message"]


def test_delete_alert_removes_it(client: TestClient) -> None:
    alert = create_alert(client)

    assert client.delete(f"/alerts/{alert['id']}").status_code == 204
    assert client.get(f"/alerts/{alert['id']}").status_code == 404
