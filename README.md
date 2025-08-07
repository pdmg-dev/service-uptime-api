# 🔧 Service Uptime & Health Checker API

A production-ready FastAPI backend that monitors the uptime and response health of registered websites and APIs. Features include periodic checks, historical logs, uptime analytics, JWT authentication, and optional alerting via email or Telegram.

## 💡 Key Features

- 🕒 Periodic service checks with async HTTP requests
- 📊 Uptime statistics and historical logs stored in PostgreSQL
- 🔐 JWT-based user authentication
- 🚨 Optional alerts for downtime events
- ⚡ Redis caching for fast status retrieval
- 📈 Ready for deployment on Render, Railway, or Heroku

## 🚀 Tech Stack

FastAPI · SQLAlchemy · PostgreSQL · Redis · Celery · httpx · JWT