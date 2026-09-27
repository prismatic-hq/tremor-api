import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, status
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from tremor_api import alerts
from tremor_api.config import DatabaseSettings
from tremor_api.db import build_engine, build_session_factory

PROBE_PATHS = ["/healthz", "/readyz", "/metrics"]
logger = logging.getLogger(__name__)


def create_app(settings: DatabaseSettings | None = None) -> FastAPI:
    engine = build_engine(settings or DatabaseSettings())

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        yield
        engine.dispose()

    app = FastAPI(title="tremor-api", lifespan=lifespan)
    app.state.session_factory = build_session_factory(engine)
    app.include_router(alerts.router)

    @app.get("/healthz", include_in_schema=False)
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz", include_in_schema=False)
    def readyz(request: Request, response: Response) -> dict[str, str]:
        try:
            with request.app.state.session_factory() as session:
                session.execute(text("SELECT 1"))
        except SQLAlchemyError:
            logger.exception("readiness check failed: database unreachable")
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {"status": "database unavailable"}
        return {"status": "ok"}

    Instrumentator(excluded_handlers=PROBE_PATHS).instrument(app).expose(
        app, endpoint="/metrics", include_in_schema=False
    )
    return app
