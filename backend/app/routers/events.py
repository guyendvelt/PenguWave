"""Event endpoints. All require authentication; any authenticated role may read
(ADR-4: admin and viewer both have read access to events)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.db import get_session
from app.core.deps import get_current_user
from app.models.event import Event
from app.models.user import User
from app.schemas.event import EventPublic

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=list[EventPublic])
def list_events(
    session: Session = Depends(get_session),
    _user: User = Depends(get_current_user),
) -> list[Event]:
    return session.exec(select(Event).order_by(Event.timestamp.desc())).all()


@router.get("/{event_id}", response_model=EventPublic)
def get_event(
    event_id: str,
    session: Session = Depends(get_session),
    _user: User = Depends(get_current_user),
) -> Event:
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    return event
