import os

from fastapi import FastAPI, HTTPException

from heroes_api import bookings, db
from heroes_api.invoices import generate_invoice
from heroes_api.models import BookingIn, ClientIn, TierChange


def create_app(db_path: str | None = None) -> FastAPI:
    app = FastAPI(title="Mettle & Co hero bookings")
    conn = db.connect(db_path or os.environ.get("HEROES_DB", "heroes.db"))
    db.init_db(conn)

    def get_client_row(client_id: int):
        row = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="client not found")
        return row

    @app.post("/clients", status_code=201)
    def create_client(client: ClientIn):
        cursor = conn.execute(
            "INSERT INTO clients (name, plan, seats, contact_email) VALUES (?, ?, ?, ?)",
            (client.name, client.plan, client.seats, client.contact_email),
        )
        conn.commit()
        return dict(get_client_row(cursor.lastrowid))

    @app.get("/clients")
    def list_clients():
        return [dict(row) for row in conn.execute("SELECT * FROM clients ORDER BY id")]

    @app.post("/clients/{client_id}/tier")
    def change_tier(client_id: int, change: TierChange):
        get_client_row(client_id)
        conn.execute("UPDATE clients SET plan = ? WHERE id = ?", (change.plan, client_id))
        conn.commit()
        return dict(get_client_row(client_id))

    @app.get("/heroes")
    def list_heroes():
        return [dict(row) for row in conn.execute("SELECT name, power FROM heroes ORDER BY id")]

    @app.post("/bookings", status_code=201)
    def create_booking(booking: BookingIn):
        try:
            return bookings.create_booking(conn, booking)
        except bookings.NotFound as error:
            raise HTTPException(status_code=404, detail=str(error))

    @app.get("/clients/{client_id}/bookings")
    def list_bookings(client_id: int):
        get_client_row(client_id)
        return bookings.list_bookings(conn, client_id)

    @app.get("/clients/{client_id}/invoices/{month}")
    def invoice(client_id: int, month: str):
        return generate_invoice(conn, get_client_row(client_id), month)

    return app

