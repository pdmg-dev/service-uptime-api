# 🛠️ Service Uptime & Health Checker API (MVP)

A FastAPI-based backend service that allows users to register web services, list them, and check their real-time availability and response time. Built with SQLAlchemy, Alembic-ready models, and async HTTP checks via `httpx`.

> This project is an MVP focused on core functionality. Future upgrades are still in progress.

## 🚀 Features

- **Register Services**: Add services with name and URL.
- **List Services**: Retrieve all registered services.
- **Check Service Status**: Perform live health checks and log status + response time.
- **Async Health Checks**: Efficient non-blocking HTTP requests.
- **Database Logging**: Persist service metadata and status history.


## 📦 Tech Stack

| Layer         | Technology                  |
|---------------|-----------------------------|
| Framework     | FastAPI                     |
| ORM           | SQLAlchemy                  |
| HTTP Client   | httpx (async)               |
| DB            | PostgreSQL (via SQLAlchemy) |
| Env Mgmt      | python-dotenv               |
| Migrations    | Alembic-ready               |


## 📁 Project Structure

```bash
app/ 
├── main.py             # FastAPI app entrypoint 
├── database.py         # DB engine & session setup
├── models.py           # SQLAlchemy models
├── schemas.py          # Pydantic schemas
├── routers/ 
│   └── services.py     # API routes for service management 
└── utils/
    └── healthcheck.py  # Async service status checker
```

## 🧪 API Endpoints

### ➕ Create a Service

`POST /services/`

```json
{
  "name": "Example Service",
  "url": "https://example.com"
}
```

Response:
```json
{
  "id": 1,
  "name": "Example Service",
  "url": "https://example.com"
}
```

### 📋 List All Services

`GET /services/`

Response:
```json
[
  {
    "id": 1,
    "name": "Example Service",
    "url": "https://example.com"
  }
]
```

### 🔍 Check Service Status

`GET /services/{service_id}/status`

Response:
```json
{
  "service": "Example Service",
  "status": "UP",
  "response_time_ms": 123.45
}
```

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

## 🧹 Alembic Migrations (Optional)

If you're using Alembic for migrations:
```bash
alembic init alembic
# Configure alembic.ini and env.py
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 📌 Notes
- Health checks are performed asynchronously with a 5-second timeout.
- Status logs are stored in the service_status table with timestamps.
- Duplicate service URLs are prevented via a unique constraint.

## 📄 License

MIT License. Feel free to use, modify, and contribute!

## 👨‍💻 Author

Built by Philip — backend engineer passionate about scalable systems and clean architecture.