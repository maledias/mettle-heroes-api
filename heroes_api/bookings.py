import sqlite3
from datetime import datetime

from heroes_api.models import BookingIn


class NotFound(Exception):
    pass


def hours_between(start: str, end: str) -> float:
    delta = datetime.fromisoformat(end) - datetime.fromisoformat(start)
    return delta.total_seconds() / 3600


def to_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "client_id": row["client_id"],
        "hero": row["hero"],
        "mission": row["mission"],
        "start": row["start"],
        "end": row["end"],
        "hours": hours_between(row["start"], row["end"]),
    }


def create_booking(conn: sqlite3.Connection, booking: BookingIn) -> dict:
    if conn.execute("SELECT 1 FROM clients WHERE id = ?", (booking.client_id,)).fetchone() is None:
        raise NotFound("client not found")
    hero = conn.execute("SELECT id FROM heroes WHERE name = ?", (booking.hero,)).fetchone()
    if hero is None:
        raise NotFound("hero not found")

    cursor = conn.execute(
        "INSERT INTO bookings (client_id, hero_id, mission, start, end) VALUES (?, ?, ?, ?, ?)",
        (
            booking.client_id,
            hero["id"],
            booking.mission,
            booking.start.isoformat(timespec="minutes"),
            booking.end.isoformat(timespec="minutes"),
        ),
    )
    conn.commit()
    return get_booking(conn, cursor.lastrowid)


BOOKING_QUERY = """
SELECT b.id, b.client_id, h.name AS hero, b.mission, b.start, b.end
FROM bookings b JOIN heroes h ON h.id = b.hero_id
"""


def get_booking(conn: sqlite3.Connection, booking_id: int) -> dict:
    row = conn.execute(BOOKING_QUERY + " WHERE b.id = ?", (booking_id,)).fetchone()
    return to_dict(row)


def list_bookings(conn: sqlite3.Connection, client_id: int) -> list[dict]:
    rows = conn.execute(BOOKING_QUERY + " WHERE b.client_id = ? ORDER BY b.id", (client_id,)).fetchall()
    return [to_dict(row) for row in rows]
