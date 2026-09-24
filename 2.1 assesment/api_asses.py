

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database_asses import get_session
from schemas_asses import Event, Reservation


router = APIRouter()


def validate_event(event: Event):
    if not event.title.strip():
        raise HTTPException(
            status_code=422,
            detail="Event title must not be empty"
        )

    if not event.venue.strip():
        raise HTTPException(
            status_code=422,
            detail="Venue must not be empty"
        )

    if event.capacity <= 0:
        raise HTTPException(
            status_code=422,
            detail="Capacity must be greater than 0"
        )

    if not event.organizer.strip():
        raise HTTPException(
            status_code=422,
            detail="Organizer must not be empty"
        )

    if event.status not in {"Open", "Closed"}:
        raise HTTPException(
            status_code=422,
            detail="Status must be Open or Closed"
        )


def validate_email(email: str):
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not re.match(pattern, email):
        raise HTTPException(
            status_code=422,
            detail="Invalid email address"
        )



@router.post("/events", response_model=Event, status_code=201)
def create_event(
    event: Event,
    session: Session = Depends(get_session)
):
    validate_event(event)

    session.add(event)
    session.commit()
    session.refresh(event)

    return event


@router.get("/events", response_model=list[Event])
def get_events(
    session: Session = Depends(get_session)
):
    events = session.exec(select(Event)).all()

    return events


@router.get("/events/{event_id}", response_model=Event)
def get_event(
    event_id: int,
    session: Session = Depends(get_session)
):
    event = session.get(Event, event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    return event


@router.put("/events/{event_id}", response_model=Event)
def update_event(
    event_id: int,
    updated_event: Event,
    session: Session = Depends(get_session)
):
    validate_event(updated_event)

    event = session.get(Event, event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    event.title = updated_event.title
    event.venue = updated_event.venue
    event.capacity = updated_event.capacity
    event.organizer = updated_event.organizer
    event.status = updated_event.status

    session.add(event)
    session.commit()
    session.refresh(event)

    return event


@router.delete("/events/{event_id}")
def delete_event(
    event_id: int,
    session: Session = Depends(get_session)
):
    event = session.get(Event, event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    reservations = session.exec(
        select(Reservation).where(
            Reservation.event_id == event_id
        )
    ).all()

    for reservation in reservations:
        session.delete(reservation)

    session.delete(event)
    session.commit()

    return {
        "message": "Event deleted successfully",
        "event_id": event_id
    }


@router.post(
    "/events/{event_id}/reserve",
    response_model=Reservation,
    status_code=201
)
def create_reservation(
    event_id: int,
    reservation: Reservation,
    session: Session = Depends(get_session)
):

    # 1. Check whether event exists
    event = session.get(Event, event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    # 2. Check whether event is open
    if event.status != "Open":
        raise HTTPException(
            status_code=400,
            detail="Reservations are closed for this event"
        )

    # Validate student name
    if not reservation.student_name.strip():
        raise HTTPException(
            status_code=422,
            detail="Student name must not be empty"
        )

    # Validate email
    validate_email(reservation.email)

    # Make sure reservation uses the correct event ID
    reservation.event_id = event_id

    # 3. Count existing reservations
    statement = select(Reservation).where(
        Reservation.event_id == event_id
    )

    existing_reservations = session.exec(statement).all()

    booked = len(existing_reservations)

    # 4. Prevent overbooking
    if booked >= event.capacity:
        raise HTTPException(
            status_code=400,
            detail="Event is full. No more reservations are allowed."
        )

    # Create reservation
    session.add(reservation)
    session.commit()
    session.refresh(reservation)

    return reservation



@router.get(
    "/events/{event_id}/reservations",
    response_model=list[Reservation]
)
def get_event_reservations(
    event_id: int,
    session: Session = Depends(get_session)
):

    event = session.get(Event, event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    statement = select(Reservation).where(
        Reservation.event_id == event_id
    )

    reservations = session.exec(statement).all()

    return reservations

@router.delete("/reservations/{reservation_id}")
def delete_reservation(
    reservation_id: int,
    session: Session = Depends(get_session)
):

    reservation = session.get(
        Reservation,
        reservation_id
    )

    if not reservation:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found"
        )

    session.delete(reservation)
    session.commit()

    return {
        "message": "Reservation cancelled successfully",
        "reservation_id": reservation_id
    }



@router.get("/events/{event_id}/availability")
def get_availability(
    event_id: int,
    session: Session = Depends(get_session)
):

    event = session.get(Event, event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    statement = select(Reservation).where(
        Reservation.event_id == event_id
    )

    reservations = session.exec(statement).all()

    booked = len(reservations)
    remaining = event.capacity - booked

    return {
        "capacity": event.capacity,
        "booked": booked,
        "remaining": remaining
    }