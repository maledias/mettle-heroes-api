import pytest

WINDOW = {"start": "2026-09-14T10:00", "end": "2026-09-14T12:00"}


def book(client, client_id, hero="Brisk", start="2026-09-14T09:00", end="2026-09-14T12:00"):
    response = client.post(
        "/bookings",
        json={"client_id": client_id, "hero": hero, "start": start, "end": end, "mission": "Market patrol"},
    )
    assert response.status_code == 201
    return response


def available_names(client, start=WINDOW["start"], end=WINDOW["end"]):
    response = client.get("/heroes/available", params={"start": start, "end": end})
    assert response.status_code == 200
    return [hero["name"] for hero in response.json()]


def test_every_hero_is_free_when_nothing_is_booked(client):
    response = client.get("/heroes/available", params=WINDOW)

    assert response.status_code == 200
    assert response.json() == client.get("/heroes").json()


@pytest.mark.parametrize(
    "start, end",
    [
        ("2026-09-14T09:00", "2026-09-14T11:00"),  # overlaps the window's start
        ("2026-09-14T11:00", "2026-09-14T13:00"),  # overlaps the window's end
        ("2026-09-14T10:30", "2026-09-14T11:30"),  # inside the window
        ("2026-09-14T08:00", "2026-09-14T14:00"),  # covers the whole window
    ],
)
def test_a_hero_with_an_overlapping_booking_is_not_free(client, harbour_council, start, end):
    book(client, harbour_council["id"], hero="Findwell", start=start, end=end)

    names = available_names(client)

    assert "Findwell" not in names
    assert len(names) == 14


def test_a_booking_that_ends_when_the_window_starts_leaves_the_hero_free(client, harbour_council):
    book(client, harbour_council["id"], hero="Findwell", start="2026-09-14T08:00", end="2026-09-14T10:00")

    assert "Findwell" in available_names(client)


def test_a_booking_that_starts_when_the_window_ends_leaves_the_hero_free(client, harbour_council):
    book(client, harbour_council["id"], hero="Findwell", start="2026-09-14T12:00", end="2026-09-14T14:00")

    assert "Findwell" in available_names(client)


def test_a_booking_on_another_day_leaves_the_hero_free(client, harbour_council):
    book(client, harbour_council["id"], hero="Findwell", start="2026-09-15T10:00", end="2026-09-15T12:00")

    assert "Findwell" in available_names(client)


def test_bookings_from_every_client_count(client, harbour_council):
    other = client.post("/clients", json={"name": "Wrenfield Town Council", "plan": "Pro", "seats": 3}).json()
    book(client, harbour_council["id"], hero="Quorum", start="2026-09-14T10:00", end="2026-09-14T11:00")
    book(client, other["id"], hero="Pivot", start="2026-09-14T11:00", end="2026-09-14T12:00")

    names = available_names(client)

    assert "Quorum" not in names
    assert "Pivot" not in names
    assert len(names) == 13


@pytest.mark.parametrize(
    "start, end",
    [
        ("2026-09-14T12:00", "2026-09-14T10:00"),  # ends before it starts
        ("2026-09-14T10:00", "2026-09-14T10:00"),  # empty window
    ],
)
def test_window_must_end_after_it_starts(client, start, end):
    response = client.get("/heroes/available", params={"start": start, "end": end})

    assert response.status_code == 422


@pytest.mark.parametrize(
    "params",
    [
        {"end": "2026-09-14T12:00"},
        {"start": "2026-09-14T10:00"},
        {"start": "next tuesday", "end": "2026-09-14T12:00"},
    ],
)
def test_window_needs_a_valid_start_and_end(client, params):
    response = client.get("/heroes/available", params=params)

    assert response.status_code == 422
