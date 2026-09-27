import uuid

import httpx2 as httpx
from fastapi import Request

from tremor_api.config import StewardSettings

HIGHEST_PRIORITY = "high"


class StewardUnavailable(Exception):
    pass


class StewardClient:
    def __init__(self, settings: StewardSettings) -> None:
        self._timeout = settings.timeout_seconds
        self._http = httpx.Client(base_url=settings.url, timeout=settings.timeout_seconds)

    def open_inspection(self, station: str, alert_id: uuid.UUID) -> uuid.UUID:
        payload = {
            "site": station,
            "title": f"Inspect {station}: critical alert",
            "priority": HIGHEST_PRIORITY,
            "source_alert_id": str(alert_id),
        }
        try:
            response = self._http.post("/work-orders", json=payload)
            response.raise_for_status()
            return uuid.UUID(response.json()["id"])
        except httpx.TimeoutException as error:
            raise StewardUnavailable(f"timed out after {self._timeout}s") from error
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            raise StewardUnavailable(f"POST /work-orders returned {status}") from error
        except httpx.HTTPError as error:
            raise StewardUnavailable(f"{type(error).__name__}: {error}") from error
        except (KeyError, ValueError) as error:
            raise StewardUnavailable(f"invalid work order response: {error}") from error

    def close(self) -> None:
        self._http.close()


def get_steward(request: Request) -> StewardClient:
    return request.app.state.steward
