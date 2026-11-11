from tests.test_bookings import book

WINDOW = {"start": "2026-12-31T09:00", "end": "2026-12-31T12:00"}


def available(client, **window):
    response = client.get("/heroes/available", params=window or WINDOW)
    assert response.status_code == 200
    return [h["name"] for h in response.json()]


def test_every_hero_is_free_when_nothing_is_booked(client):
    assert len(available(client)) == 15


def test_a_hero_booked_inside_the_window_is_not_free(client, harbour_council):
    book(client, harbour_council["id"], hero="Brisk", start="2026-12-31T10:00", end="2026-12-31T11:00")

    names = available(client)

    assert "Brisk" not in names
    assert len(names) == 14


def test_a_booking_that_ends_when_the_window_starts_leaves_the_hero_free(client, harbour_council):
    book(client, harbour_council["id"], hero="Brisk", start="2026-12-31T07:00", end="2026-12-31T09:00")

    assert "Brisk" in available(client)


def test_a_booking_that_starts_when_the_window_ends_leaves_the_hero_free(client, harbour_council):
    book(client, harbour_council["id"], hero="Brisk", start="2026-12-31T12:00", end="2026-12-31T14:00")

    assert "Brisk" in available(client)


def test_a_booking_that_covers_the_whole_window_makes_the_hero_busy(client, harbour_council):
    book(client, harbour_council["id"], hero="Brisk", start="2026-12-31T08:00", end="2026-12-31T13:00")

    assert "Brisk" not in available(client)


def test_window_must_end_after_it_starts(client):
    response = client.get("/heroes/available", params={"start": "2026-12-31T12:00", "end": "2026-12-31T09:00"})

    assert response.status_code == 422


def test_board_page_is_served(client):
    response = client.get("/board")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
