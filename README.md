# 🛠️ Service Uptime API (MVP)

A FastAPI-based backend service that lets users register websites or APIs, check their availability in real-time, and track performance history.
It includes authentication, background polling, dashboard endpoints, and automatic cleanup of old data.

> This is an MVP version, but the architecture is ready for production-grade enhancements.

## 🚀 Features

- User Authentication with JWT-based access tokens.
- Register Services with unique URL per user and optional keyword validation.
- List Services with metadata.
- Check Service Status on demand.
- Async Background Polling: Periodically checks all active services in the background.
- Status Classification: Detects UP, DOWN, SLOW, UNREACHABLE, and other states.
- Dashboard Endpoint: Returns latest status for all services.
- Automatic Cleanup of old status records.
- SQLite/PostgreSQL support (configurable via .env)

## 📦 Tech Stack

| Layer       | Technology                       |
| ----------- | -------------------------------- |
| Framework   | FastAPI                          |
| ORM         | SQLAlchemy                       |
| DB          | SQLite / PostgreSQL (via URL)    |
| HTTP Client | httpx (async)                    |
| Auth        | OAuth2 + JWT (via `python-jose`) |
| Passwords   | bcrypt (via `passlib`)           |
| Env Mgmt    | pydantic-settings (`.env` file)  |
| Migrations  | Alembic-ready models             |
| Scheduler   | asyncio background task          |

## 📁 Project Structure

```bash
app/
├── core/                # Config, DB, security, logging
├── models/              # SQLAlchemy models (User, Service, ServiceStatus)
├── repositories/        # DB access layer
├── routers/             # API route handlers
├── schemas/             # Pydantic models
├── services/            # Business logic, polling, cleanup
└── main.py              # FastAPI entry point
run.py                   # Uvicorn launcher
```

## 🧪 API Endpoints

### Auth
- `POST /auth/register` → Register new user.
- `POST /auth/login` → Get JWT token.

### Services (Auth Required)
- `POST /services/` → Register a service.
- `GET /services/` → List all services for current user.
- `PATCH /services/{id}/` → Update service info.
- `DELETE /services/{id}/` → Delete service.
- `GET /services/{id}/status` → Check status now.
- `GET /services/{id}/status/history` → View last 10 checks.

### Public Dashboard
- `GET /status/dashboard` → Latest status for all services.

### Health Check
- `GET /health` → Scheduler health info.

## 🛠️ Setup & Run

1. Clone the repo
```bash
git clone https://github.com/your-username/service-uptime-api.git
cd service-uptime-api
```

2. Create .env
```env
DATABASE_URL=postgresql://user:password@localhost:5432/your_db
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the server
```bash
python run.py
```

5. Access API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Background Polling
- Runs every POLL_INTERVAL_SECONDS (default: 60s).
- Checks all active services asynchronously.
- Saves results in service_status table.
- Deletes statuses older than 30 days.

## 📌 Notes
- Unique (url, user_id) constraint prevents duplicate registrations per user.
- JWT tokens expire based on ACCESS_TOKEN_EXPIRE_MINUTES.
- Optional keyword matching ensures response content contains expected text.
- Supports both SQLite (dev) and PostgreSQL (prod).

## 📄 License

MIT License. Feel free to use, modify, and contribute!

## 👨‍💻 Author

Built by Philip — backend engineer passionate about scalable systems and clean architecture.
