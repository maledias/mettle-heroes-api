# Mettle & Co hero bookings

The booking and dispatch API for Mettle & Co. Clients book heroes for missions and get a monthly invoice. FastAPI and SQLite, Python 3.12.

## Commands

- Install: `uv sync`
- Test: `uv run pytest`
- Run: `uv run uvicorn --factory heroes_api.main:create_app --reload`, then open http://127.0.0.1:8000/docs

## Layout

- `heroes_api/main.py`: the app and its routes
- `heroes_api/bookings.py`: creating and listing bookings
- `heroes_api/invoices.py`: monthly invoices
- `heroes_api/db.py`: the schema and the 15 heroes
- `tests/`: one test file per area

## Team rules

- Nothing is built without an approved plan. Plan first, then code.
- Write the failing test first, show it fail, then write the code.
- Never edit an existing test to make it pass.
- Run `uv run pytest` after every change.
- Keep specs and plans out of the repository. The pull request description holds the goal, the approach and the main decisions, and links the issue.
- Commit messages are one line, under 60 characters.
- A person reviews every pull request before it is merged.
