# Visitor Management System

A lightweight visitor management system: staff sign up, log in, register
visitors, and check them in/out with a photo. Built with FastAPI, SQLAlchemy,
and a small vanilla-JS front end.

## Features

- Staff authentication (signup / login) with hashed passwords and JWT bearer tokens
- Visitor registration with server-side validation and a live password-strength checklist
- Registration timestamp recorded per visitor, alongside check-in/check-out
- Photo-verified check-in and check-out, with a live visitor look-up and photo preview before acting
- Visitor directory with search, status filter, sortable columns, pagination, and CSV export
- Full visitor profile page: details, both photos, in-place edit, delete, printable view
- Public "find my visit" look-up by visitor ID + email (no login required)
- Account settings page (view profile, change password)
- Dashboard overview: live stats, recent activity feed, quick-action links
- Toast notifications and an in-app confirm dialog instead of browser pop-ups
- Branded favicon, page descriptions, footer, and 404 page throughout
- Audit trail: every visitor record shows which staff member registered,
  checked in, and checked out
- Login is rate-limited against brute-force guessing
- Uploaded photos are validated by actual file content, not just extension
- Automated test suite (pytest) covering auth, visitor CRUD, and security behaviors
- Docker / docker-compose support for containerized deployment
- Interactive API docs at `/docs` (Swagger UI) and `/redoc`

## Tech stack

- **Backend:** FastAPI, SQLAlchemy, SQLite, python-jose (JWT), passlib (password hashing)
- **Frontend:** static HTML/CSS/vanilla JS served directly by FastAPI — no build step

## Project structure

```
visitors project/
├── app/
│   ├── main.py            # FastAPI app, CORS, static mounts
│   ├── config.py          # Settings loaded from environment / .env
│   ├── database.py        # SQLAlchemy engine/session
│   ├── models.py          # User, Visitor tables
│   ├── schemas.py         # Pydantic request/response models
│   ├── security.py        # Password hashing, JWT, auth dependency
│   ├── utils.py           # Visitor ID + safe photo upload helpers
│   └── routers/
│       ├── auth.py        # /auth/signup, /auth/login
│       └── visitors.py    # /visitors/*
├── frontend/
│   ├── index.html         # Login / signup
│   ├── dashboard.html     # Overview: stats, recent activity, quick links
│   ├── register.html      # Register a new visitor
│   ├── checkin.html       # Look up a visitor, then check in/out with a photo
│   ├── visitors.html      # Directory: search, filter, paginate
│   ├── visitor.html       # Single visitor: details, photos, edit, delete
│   ├── find-visit.html    # Public look-up (no login)
│   ├── settings.html      # Account info + change password
│   ├── 404.html           # Served automatically for unknown routes
│   ├── css/style.css
│   └── js/
│       └── nav.js         # Shared top nav injected into every staff page
├── tests/                 # pytest suite (isolated in-memory DB + temp photo dirs)
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_visitors.py
├── checkin_photos/        # Uploaded check-in photos (gitignored)
├── checkout_photos/       # Uploaded check-out photos (gitignored)
├── main.py                 # `uvicorn main:app` entry point
├── requirements.txt
├── requirements-dev.txt    # requirements.txt + pytest/httpx
├── pytest.ini
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Setup

1. **Create a virtual environment** (skip if `venv/` already exists):

   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**

   ```bash
   copy .env.example .env        # Windows
   cp .env.example .env          # macOS/Linux
   ```

   Then set a real `SECRET_KEY` in `.env`:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

   If `SECRET_KEY` is left unset, the app will generate a temporary one at
   startup and print a warning — fine for a quick local test, but every
   restart invalidates existing login tokens, so set a real key before
   deploying or sharing the app.

4. **Run the server:**

   ```bash
   uvicorn main:app --reload
   ```

5. Open **http://127.0.0.1:8000/** for the web UI, or **http://127.0.0.1:8000/docs**
   for the interactive API docs.

## API overview

| Method | Path                              | Auth  | Description                          |
|--------|------------------------------------|-------|---------------------------------------|
| POST   | `/auth/signup`                     | —     | Create a staff account                |
| POST   | `/auth/login`                      | —     | Log in, returns a bearer token        |
| GET    | `/auth/me`                         | staff | Get the logged-in staff profile       |
| PUT    | `/auth/password`                   | staff | Change the logged-in staff password   |
| POST   | `/visitors`                        | staff | Register a new visitor                |
| GET    | `/visitors`                        | staff | List all visitors                     |
| GET    | `/visitors/lookup`                 | —     | Public look-up by visitor ID + email  |
| GET    | `/visitors/{id}`                   | staff | Get a single visitor's full record    |
| PUT    | `/visitors/{id}`                   | staff | Update a visitor's core details       |
| POST   | `/visitors/{id}/checkin`           | staff | Check in with a photo                 |
| PUT    | `/visitors/{id}/checkout`          | staff | Check out with a photo                |
| GET    | `/visitors/{id}/photo/{stage}`     | staff | Fetch a check-in/out photo             |
| DELETE | `/visitors/{id}`                   | staff | Delete a visitor record               |
| GET    | `/health`                          | —     | Health check                          |

"staff" routes require an `Authorization: Bearer <token>` header, obtained
from `/auth/login`. The web UI handles this automatically once you log in.

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

Each test runs against its own in-memory SQLite database and a temp photo
directory (via fixture overrides in `tests/conftest.py`) — the suite never
touches your real `visitor.db` or `checkin_photos`/`checkout_photos`.

## Running with Docker

```bash
cp .env.example .env   # set a real SECRET_KEY first
docker compose up --build
```

This builds the image, mounts `visitor.db` and the photo folders from the
host so data survives container restarts, and serves the app on
**http://localhost:8000/**.

## Security notes

This project previously had a few gaps that are now fixed:

- The JWT secret is no longer hardcoded in source — it's read from `SECRET_KEY`
  in the environment.
- Visitor creation, listing, check-in/out, photo access, and deletion now
  require a valid staff bearer token (previously anyone could call them).
- Uploaded photo filenames are never taken from the client — they're
  regenerated server-side, and both file extension and size are validated,
  closing a path-traversal / arbitrary-upload gap.
- Uploaded photos are also checked against their actual magic bytes, not
  just their extension, so a non-image file can't be disguised as a `.jpg`.
- Login no longer distinguishes "wrong email" from "wrong password" in its
  error message, to avoid leaking which emails are registered.
- Login is rate-limited (5 failed attempts per IP+email locks out for 60
  seconds) to slow down brute-force password guessing. This guard is
  in-process and per-worker — fine for a single-instance deployment, but a
  multi-worker/multi-instance setup would need a shared store (e.g. Redis)
  for it to be effective across all of them.

## Notes on API changes

If you had another client calling the old routes (`/visitor/create`,
`/visitor/checkin/{id}`, `/visitor/checkout/{id}`, `/logout`), they've been
renamed/removed as part of this cleanup:

- `/visitor/create` → `POST /visitors`
- `/visitor/checkin/{id}` → `POST /visitors/{id}/checkin`
- `/visitor/checkout/{id}` → `PUT /visitors/{id}/checkout`
- `/visitors?visitor_id=&email=` → `GET /visitors/lookup?visitor_id=&email=`
- `/logout` was removed — it didn't invalidate anything (JWTs are stateless),
  it just re-ran the same look-up as `/visitors/lookup`. The dashboard now
  "logs out" by discarding the token client-side.

## Possible next steps

- Live webcam capture instead of file picker (`getUserMedia`)
- Per-user visitor scoping if multiple organizations share one instance
- Swap SQLite for PostgreSQL for multi-instance deployments
