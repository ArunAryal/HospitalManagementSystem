# Hospital Management System

A REST API backend for managing hospital operations built with FastAPI and MySQL.

![Python](https://img.shields.io/badge/Python-3.14+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.129+-009688?logo=fastapi&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-MariaDB-003545?logo=mariadb&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- Patient registration and record management
- Doctor profiles with specialization and availability tracking
- Appointment booking with conflict detection
- Medical records and prescription management
- Room and inpatient admission management
- Billing and payment tracking

## Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **Pydantic v2** — data validation
- **MariaDB / MySQL** — database
- **Uvicorn** — ASGI server

## Getting Started

### Prerequisites

- Python 3.14+
- MariaDB or MySQL
- [uv](https://github.com/astral-sh/uv)

### Installation

```bash
git clone <repo-url>
cd hospital-management-system
uv sync
```

### Database setup

```bash
mariadb -u <user> -p < database/schema.sql
```

### Environment variables

Create `backend/.env`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=hospital_management
```

### Run

```bash
uv run uvicorn backend.main:app --reload
```

API is available at `http://localhost:8000`.  
Interactive docs at `http://localhost:8000/docs`.

## API Overview

| Resource | Base path |
|---|---|
| Patients | `/patients` |
| Doctors | `/doctors` |
| Appointments | `/appointments` |
| Medical Records | `/medical-records` |
| Medicines & Prescriptions | `/medicines` |
| Rooms, Admissions & Billing | `/billing` |

Full endpoint reference is available at `/docs` (Swagger UI) or `/redoc` once the server is running.

## Project Structure

```
backend/
├── main.py           # App entry point
├── database.py       # DB connection and session
├── models.py         # SQLAlchemy models
├── schemas.py        # Pydantic schemas
└── routers/          # One file per resource group
database/
└── schema.sql        # Schema, triggers, views, stored procedures
```

## Known Limitations

- No authentication — all endpoints are currently public
- No patient search by name or phone
- Departments and staff tables exist in the DB but have no API endpoints yet
- Hard deletes only — no soft delete / archive support