"""Add two clients and ten bookings on 31 December 2026 to a running hero bookings API.

Start the API on a fresh database first, then run: python3 seed_bookings.py
Six heroes end up busy between 09:00 and 12:00. Two more have bookings that only
touch that window, so they stay free.
"""

import json
import urllib.request

API = "http://127.0.0.1:8000"

CLIENTS = [
    {"name": "Brindlemouth Harbour Council", "plan": "Max", "seats": 10},
    {"name": "Wrenfield Town Council", "plan": "Enterprise", "seats": 22},
]

# (client, hero, mission, start, end). Times are on 2026-12-31.
BOOKINGS = [
    (1, "Merge Lane", "Clear the Eastgate bridge queue", "08:00", "10:00"),
    (1, "Lowtide", "Drain the harbour car park", "09:30", "11:30"),
    (1, "Forecaster", "Call the weather for the fireworks barge", "11:00", "13:00"),
    (2, "Quorum", "Get the council budget vote over the line", "09:00", "12:00"),
    (2, "Thermostat", "Keep the town hall at 20 degrees", "07:00", "17:00"),
    (2, "Findwell", "Find the mayor's chain of office", "10:00", "10:30"),
    (1, "Brisk", "Deliver the harbour master's keys", "07:00", "09:00"),
    (2, "Pivot", "Check the year-end spreadsheet", "12:00", "14:00"),
    (1, "Late Shift", "Watch the harbour overnight", "23:00", "23:59"),
    (2, "Paperweight", "Hold down the New Year marquee", "14:00", "18:00"),
]


def post(path: str, body: dict) -> dict:
    request = urllib.request.Request(
        API + path,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)


for client in CLIENTS:
    post("/clients", client)

for client_id, hero, mission, start, end in BOOKINGS:
    post("/bookings", {
        "client_id": client_id,
        "hero": hero,
        "mission": mission,
        "start": f"2026-12-31T{start}",
        "end": f"2026-12-31T{end}",
    })

print(f"Added {len(CLIENTS)} clients and {len(BOOKINGS)} bookings on 31 December 2026.")
