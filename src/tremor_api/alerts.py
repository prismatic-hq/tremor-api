import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from tremor_api.db import get_session
from tremor_api.models import Alert
from tremor_api.schemas import AlertCreate, AlertRead, AlertUpdate

router = APIRouter(prefix="/alerts", tags=["alerts"])
SessionDep = Annotated[Session, Depends(get_session)]


def _get_or_404(session: Session, alert_id: uuid.UUID) -> Alert:
    alert = session.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"alert {alert_id} not found")
    return alert


@router.post("", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
def create_alert(payload: AlertCreate, session: SessionDep) -> Alert:
    alert = Alert(**payload.model_dump())
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return alert


@router.get("", response_model=list[AlertRead])
def list_alerts(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Alert]:
    query = select(Alert).order_by(Alert.created_at, Alert.id).limit(limit).offset(offset)
    return list(session.scalars(query))


@router.get("/{alert_id}", response_model=AlertRead)
def get_alert(alert_id: uuid.UUID, session: SessionDep) -> Alert:
    return _get_or_404(session, alert_id)


@router.patch("/{alert_id}", response_model=AlertRead)
def update_alert(alert_id: uuid.UUID, payload: AlertUpdate, session: SessionDep) -> Alert:
    alert = _get_or_404(session, alert_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(alert, field, value)
    session.commit()
    session.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(alert_id: uuid.UUID, session: SessionDep) -> None:
    session.delete(_get_or_404(session, alert_id))
    session.commit()
