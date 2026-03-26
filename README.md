# Hospital Management System

A full-stack Hospital Management System built with **FastAPI** (backend) and **Next.js** (frontend). Manage patients, doctors, appointments, medical records, inventory, rooms, and billing in one integrated platform.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.129+-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16.2+-black?logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/React-18-61dafb?logo=react&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-MariaDB-003545?logo=mariadb&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Patient Management** — CRUD, search, medical history, appointments, bills, and analytics
- **Doctor Management** — Profiles, specialization, fees, and availability tracking
- **Appointment Booking** — Schedule with conflict detection, filtering, and status tracking
- **Medical Records** — Complete patient history with prescriptions and diagnoses
- **Inventory Management** — Medicine tracking, stock alerts, and expiry dates
- **Room & Admissions** — Room management, occupancy tracking, and discharge workflows
- **Billing & Payments** — Auto-generated bills, payment recording, and financial analytics
- **Dashboard** — Real-time statistics, quick actions, and activity feed
- **Responsive UI** — Mobile-friendly design with modal-based CRUD operations
- **API Documentation** — Interactive Swagger UI and ReDoc endpoints

## Tech Stack

**Backend:** FastAPI, SQLAlchemy 2.0, Pydantic v2, MySQL/MariaDB, Uvicorn, Python 3.11+  
**Frontend:** Next.js 16.2, React 18, TypeScript 5, Tailwind CSS, Lucide Icons, Recharts  
**Testing:** pytest, pytest-asyncio, httpx  
**Package Manager:** uv

## Architecture

**Backend:** Routes → Services (Business Logic) → Repositories (Data Access) → SQLAlchemy ORM → Database

**Frontend:** Pages → Components → Custom Hooks → API Client → Backend

Key patterns: Separation of concerns, dependency injection, repository pattern, custom exceptions, middleware error handling, Pydantic validation.

## Database Schema

Core tables: patients, doctors, departments, appointments, medical_records, medicines, prescriptions, rooms, admissions, bills

Key relationships: Appointments link patients to doctors • Medical records capture consultations • Prescriptions link records to medicines • Admissions manage room occupancy • Bills aggregate charges

## Quick Start

### Prerequisites
- Python 3.11+, Node.js 18+, MariaDB/MySQL, [uv](https://github.com/astral-sh/uv)

### 1. Clone & Setup

```bash
git clone https://github.com/ArunAryal/HospitalManagementSystem.git
cd Hospital\ Management\ System

# Create .env file (copy from .env.example)
cp .env.example .env
```

### 2. Backend

```bash
# Install dependencies
uv sync

# Setup database
mariadb -u <user> -p < database/schema.sql

# Run server
uv run uvicorn backend.main:app --reload
```

Backend runs at `http://localhost:8000` with docs at `/docs` and `/redoc`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`

### 4. Run Tests

```bash
uv run pytest tests/ -v
```

## Project Structure

```
backend/                # FastAPI REST API
├── routers/           # Resource endpoints (patients, doctors, appointments, etc.)
├── services/          # Business logic layer
├── models.py          # SQLAlchemy ORM models
├── schemas.py         # Pydantic validation schemas
├── repositories.py    # Data access layer
└── middleware.py      # Error handling

frontend/              # Next.js dashboard
├── app/              # Pages for each resource
├── components/       # Reusable React components
├── hooks/            # Custom hooks (useData, useAsync, useValidation)
├── lib/              # API client and utilities
└── types/            # TypeScript definitions

database/
└── schema.sql        # Database schema with triggers, indexes, views

tests/                # Pytest test suite
```



## API Documentation

Once the server is running:
- **Swagger UI** — `http://localhost:8000/docs`
- **ReDoc** — `http://localhost:8000/redoc`
- **Health Check** — `http://localhost:8000/health`

Full interactive API docs with request/response examples and try-it-out functionality.

## Status & Limitations

✅ **Complete:** All CRUD operations, search, filtering, pagination, relationships, appointment conflict detection, billing with auto-generation, payments, inventory, room occupancy, admission workflows, stats endpoints, responsive UI, API docs, error handling, logging, test suite.

⚠️ **Limitations:** No authentication/authorization, no audit logging, no file uploads, no real-time updates (WebSocket).

🔄 **Future:** JWT auth + RBAC, advanced reports, mobile app, document management, email notifications, telemedicine.

## Troubleshooting

**Backend issues:**
- Module not found? Run `uv sync`
- Database connection? Verify MariaDB/MySQL is running and `.env` credentials are correct
- Port 8000 in use? Use `uv run uvicorn backend.main:app --port 8001 --reload`

**Frontend issues:**
- API connection? Check `NEXT_PUBLIC_API_URL` in `.env.local` and ensure backend is running
- Dependencies? Run `rm -rf node_modules && npm install`
- Port 3000 in use? Use `npm run dev -- -p 3001`

**Database issues:**
- Foreign key errors? Ensure referenced records exist before creating relationships
- Inconsistent data? Run `uv run python backend/scripts/recalculate_bills.py`

See `http://localhost:8000/health` for backend health status.



## License & Support

**License:** MIT — Open source and free to use, modify, and distribute