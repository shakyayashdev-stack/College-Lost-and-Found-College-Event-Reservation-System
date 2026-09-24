from sqlmodel import Field, SQLModel


class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    venue: str
    capacity: int
    organizer: str
    status: str


class Reservation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    event_id: int
    student_name: str
    roll_number: str
    email: str