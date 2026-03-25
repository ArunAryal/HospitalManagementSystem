# Hospital Management System

A comprehensive full-stack Hospital Management System with an integrated backend REST API and modern frontend dashboard. Built with **FastAPI** for the backend and **Next.js** for the frontend.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.129+-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16.2+-black?logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/React-18-61dafb?logo=react&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-MariaDB-003545?logo=mariadb&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178c6?logo=typescript&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

### Core Functionality
- **Patient Management** — Register, update, and search patients by name/phone; comprehensive medical history
- **Doctor Management** — Doctor profiles with specialization, availability tracking, consultation fees
- **Appointment Booking** — Schedule appointments with automatic conflict detection and status tracking
- **Medical Records** — Complete patient medical history with diagnosis, treatment, and notes
- **Prescriptions** — Full prescription management linked to medical records with dosage instructions
- **Room & Admissions** — Manage room availability, occupancy, and patient admissions/discharges
- **Billing & Payments** — Auto-generated bills with itemized charges; payment recording and status tracking
- **Inventory Management** — Medicine stock tracking, expiry dates, low-stock alerts, and reordering

### Analytics & Dashboard
- **Real-time Dashboard** — Statistics cards displaying patients, doctors, today's appointments, revenue, available rooms
- **Billing Analytics** — Total collected, outstanding, and pending amounts with status filtering
- **Inventory Stats** — Low-stock medicine alerts and inventory overview
- **Occupancy Tracking** — Room occupancy statistics and active admission monitoring
- **Recent Activity** — Dashboard widgets showing recent appointments and active admissions

### Advanced Features
- **Relationship Queries** — Get patient appointments, medical records, and bills in a single request
- **Status Filtering** — Filter appointments, bills, and admissions by status
- **Smart Search** — Patient search by name or phone with pagination
- **Availability Management** — Toggle doctor availability status
- **Bill Generation** — Auto-generate bills from admissions with detailed breakdown
- **Error Handling** — Comprehensive error handling with custom exception types and validation
- **Logging** — Structured logging with color-coded console output for debugging

### UI/UX Features
- **Responsive Design** — Mobile-friendly interface using Tailwind CSS
- **Modal Dialogs** — Seamless CRUD operations in modal workflows
- **Status Badges** — Visual status indicators for appointments, bills, and admissions
- **Loading States** — Skeleton loaders and spinners during data fetching
- **Error Boundaries** — Graceful error handling and user feedback
- **Quick Actions** — Dashboard quick action buttons for common tasks
- **Patient Detail View** — Consolidated view with appointments, medical records, and bills

## Tech Stack

### Backend
- **FastAPI** — Modern async web framework with automatic OpenAPI docs
- **SQLAlchemy 2.0** — Powerful ORM for database operations
- **Pydantic v2** — Data validation and serialization with type hints
- **MySQL/MariaDB** — Relational database for persistent storage
- **Uvicorn** — ASGI server for running async applications
- **Python 3.11+** — Modern Python with type hints and performance

### Frontend
- **Next.js 16.2** — React framework with server-side rendering and routing
- **React 18** — UI library with hooks and functional components
- **TypeScript 5** — Type-safe development with full IDE support
- **Tailwind CSS** — Utility-first CSS framework for rapid UI development
- **Lucide React** — Beautiful icon library with 300+ icons
- **Recharts** — Data visualization library for charts and graphs
- **Date-fns** — Modern date manipulation utilities

### Development & Testing
- **pytest** — Python testing framework with fixtures
- **pytest-asyncio** — Async test support
- **httpx** — Async HTTP client for API testing
- **ESLint** — JavaScript linting
- **TypeScript compiler** — Type checking

### Infrastructure
- **uv** — Fast Python package installer and resolver
- **Git** — Version control
- **Docker-ready** — Containerization support

## Architecture Patterns

### Backend Architecture
```
HTTP Request
    ↓
FastAPI Router (routers/)
    ↓
Service Layer (services/) - Business Logic
    ↓
Repository Layer (repositories.py) - Data Access
    ↓
SQLAlchemy ORM (models.py)
    ↓
MySQL Database
```

**Key Design Patterns:**
- **Separation of Concerns** — Routes, Services, Repositories
- **Dependency Injection** — FastAPI's `Depends()` for service injection
- **Repository Pattern** — Abstract data access layer
- **Custom Exceptions** — Consistent error handling
- **Middleware** — Global error handling and request logging
- **Schemas** — Pydantic models for validation

### Frontend Architecture
```
Next.js App Router
    ↓
Page Components (app/)
    ↓
Reusable Components (components/)
    ↓
Custom Hooks (hooks/)
    ↓
API Client (lib/api.ts)
    ↓
Backend API
```

**Key Patterns:**
- **Component Composition** — Reusable, modular components
- **Custom Hooks** — `useData()`, `useAsync()`, `useValidation()`
- **API Abstraction** — Centralized API client methods
- **State Management** — React hooks + local state
- **Error Boundaries** — Graceful error handling

## Database Schema Highlights

### Entity Relationships
```
Patient 1──→ Many Appointments
Patient 1──→ Many Medical Records
Patient 1──→ Many Admissions
Patient 1──→ Many Bills

Doctor 1──→ Many Appointments
Doctor 1──→ Many Medical Records

Medical Record 1──→ Many Prescriptions
Room 1──→ Many Admissions
Admission 1──→ Many Bills
```

### Indexes for Performance
- Patient name and phone (search)
- Doctor specialization (filtering)
- Appointment date and status
- Bill payment status and date
- Medicine name (search)

### Key Constraints
- Status enums for consistency (Scheduled, Completed, Cancelled)
- Payment status tracking (Pending, Paid, Partially Paid)
- Room types (General, Private, ICU, Emergency)
- Foreign keys with cascade delete for data integrity

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- MariaDB or MySQL
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- npm or yarn

### 1. Clone Repository

```bash
git clone https://github.com/ArunAryal/HospitalManagementSystem.git
cd Hospital\ Management\ System
```

### 2. Backend Setup

#### Install Dependencies
```bash
uv sync
```

#### Database Setup
```bash
mariadb -u <user> -p < database/schema.sql
```

#### Environment Variables
Create `.env` in the **project root** (not in backend folder):

```bash
# Copy from template
cp .env.example .env

# Edit with your settings
nano .env
```

Basic configuration (`.env`):
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=hospital_management
```

**Full Configuration** (optional):
```env
# Application environment
ENVIRONMENT=development  # or production
DEBUG=true              # Enable debug mode

# API Configuration  
API_TITLE=Hospital Management System API
API_VERSION=1.0.0
API_PREFIX=/api/v1

# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_secure_password
DB_NAME=hospital_management
DB_ECHO=false           # Log SQL queries (set to true for debugging)

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
CORS_CREDENTIALS=true
CORS_METHODS=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

# JWT (for future authentication)
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Pagination
PAGINATION_DEFAULT_LIMIT=100
PAGINATION_MAX_LIMIT=1000
PAGINATION_DEFAULT_SKIP=0

# Logging
LOG_LEVEL=DEBUG
```

**Note**: The `.env` file is loaded from the **project root** when running:
```bash
uv run uvicorn backend.main:app --reload
```

Never commit `.env` — it contains sensitive credentials. Use `.env.example` as a template for sharing with team members.

#### Run Backend Server
```bash
uv run uvicorn backend.main:app --reload
```

Backend API will be available at `http://localhost:8000`
- Swagger UI Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/health`

### 3. Frontend Setup

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Configure API URL (Optional)
Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Run Development Server
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

#### Build for Production
```bash
npm run build
npm start
```

## API Endpoints Overview

### Resources & Endpoints

| Resource | Base Path | Key Endpoints |
|---|---|---|
| **Patients** | `/patients` | GET, POST, PUT, DELETE, GET /search, GET /{id}/appointments, GET /{id}/medical-records, GET /{id}/bills, GET /stats |
| **Doctors** | `/doctors` | GET, POST, PUT, DELETE, GET /{id}/availability |
| **Appointments** | `/appointments` | GET, POST, PUT, DELETE, GET /{id}/cancel, GET /patient/{id}, GET /doctor/{id} |
| **Medical Records** | `/medical-records` | GET, POST, PUT, DELETE, GET /patient/{id}, GET /doctor/{id}, GET /{id}/prescriptions, POST /{id}/prescriptions |
| **Medicines** | `/medicines` | GET, POST, PUT, DELETE, GET /low-stock, GET /restock, GET /stats, GET /stats/inventory |
| **Prescriptions** | `/prescriptions` | GET, POST, DELETE (managed under medical-records) |
| **Rooms** | `/rooms` | GET, POST, PUT, DELETE, GET /available, GET /by-type/{type}, GET /stats, GET /occupancy/stats |
| **Admissions** | `/admissions` | GET, POST, PUT, DELETE, GET /patient/{id}, GET /active, POST /{id}/discharge, GET /stats |
| **Billing** | `/billing` | GET, POST, PUT, DELETE, GET /patient/{id}, POST /{id}/payment, GET /admission/{id}/generate, GET /stats, GET /stats/billing |

### Endpoint Features
- **Search & Filtering** — Patient search by name/phone, status-based filtering  
- **Pagination** — All list endpoints support `skip` and `limit` parameters
- **Relationships** — Get related data (appointments, records, bills) from patient endpoints
- **Statistics** — Dedicated stats endpoints for analytics and dashboards
- **Advanced Operations** — Cancel appointments, discharge patients, record payments, generate bills

Full endpoint documentation available at `/docs` (Swagger UI) or `/redoc` once the backend server is running.

## Project Structure

```
Hospital Management System/
├── backend/                          # FastAPI REST API backend
│   ├── main.py                       # FastAPI application entry point & router setup
│   ├── config.py                     # Configuration management using Pydantic Settings
│   ├── database.py                   # Database connection and session management
│   ├── models.py                     # SQLAlchemy ORM models for all entities
│   ├── schemas.py                    # Pydantic request/response validation schemas
│   ├── middleware.py                 # Global exception handling middleware
│   ├── exceptions.py                 # Custom exception classes for consistent error handling
│   ├── logging_config.py             # Structured logging with color support
│   ├── utils.py                      # Utility functions for validation & helpers
│   ├── repositories.py               # Base repository pattern for data access
│   ├── routers/                      # API route handlers organized by resource
│   │   ├── __init__.py
│   │   ├── patients.py               # Patient CRUD + search + stats endpoints
│   │   ├── patients_refactored.py    # Enhanced patient endpoints (alternative)
│   │   ├── doctors.py                # Doctor management + availability tracking
│   │   ├── appointments.py           # Appointment booking + conflict detection + filtering
│   │   ├── medical_records.py        # Medical records + prescriptions management
│   │   ├── medical_records_refactored.py # Enhanced medical records endpoints
│   │   ├── medicines.py              # Medicine inventory + stock tracking + reorder alerts
│   │   ├── medicines_refactored.py   # Enhanced medicine endpoints with search
│   │   ├── rooms.py                  # Room management + admissions + occupancy stats
│   │   ├── rooms_refactored.py       # Enhanced room/admission endpoints
│   │   ├── billing.py                # Billing + payments + auto-generation + stats
│   │   └── billing_refactored.py     # Enhanced billing endpoints
│   ├── services/                     # Business logic layer
│   │   ├── patient_service.py        # Patient business operations & search logic
│   │   ├── doctor_service.py         # Doctor availability & filtering logic
│   │   ├── appointment_service.py    # Appointment conflict detection & scheduling
│   │   ├── medical_records_service.py# Medical records & prescription operations
│   │   ├── medicines_service.py      # Inventory management & stock operations
│   │   ├── rooms_service.py          # Room occupancy & admission management
│   │   └── billing_service.py        # Bill generation & payment processing
│   └── scripts/                      # Database & maintenance scripts
│       ├── fix_trigger.py            # Database trigger setup utilities
│       └── recalculate_bills.py      # Billing recalculation script
│
├── frontend/                         # Next.js web dashboard
│   ├── app/                          # Next.js App Router pages
│   │   ├── layout.tsx                # Root layout with sidebar & topbar
│   │   ├── page.tsx                  # Dashboard with statistics & quick actions
│   │   ├── globals.css               # Global styles
│   │   ├── patients/                 # Patient list, detail & management pages
│   │   │   ├── page.tsx              # Patients list with search/filter
│   │   │   └── [id]/page.tsx         # Patient detail with records/appointments/bills
│   │   ├── doctors/                  # Doctor management pages
│   │   │   └── page.tsx              # Doctors list & CRUD
│   │   ├── appointments/             # Appointment pages
│   │   │   └── page.tsx              # Appointments list with filtering & status
│   │   ├── medical-records/          # Medical records & prescriptions
│   │   │   └── page.tsx              # Medical records list with filtering
│   │   ├── medicines/                # Medicine inventory pages
│   │   │   └── page.tsx              # Medicines list with stock tracking
│   │   ├── rooms/                    # Room & admission management pages
│   │   │   └── page.tsx              # Rooms, occupancy & admission tracking
│   │   └── billing/                  # Billing & payment pages
│   │       └── page.tsx              # Bills list with payment status & payment recording
│   ├── components/                   # React components
│   │   ├── layout/                   # Layout components
│   │   │   ├── Sidebar.tsx           # Navigation sidebar with menu items
│   │   │   └── Topbar.tsx            # Header with page title & user menu
│   │   ├── patients/                 # Patient components
│   │   │   └── PatientModal.tsx      # Patient CRUD modal
│   │   ├── doctors/                  # Doctor components
│   │   │   └── DoctorModal.tsx       # Doctor CRUD modal
│   │   ├── appointments/             # Appointment components
│   │   │   └── AppointmentModal.tsx  # Appointment booking modal
│   │   ├── medical-records/          # Medical record components
│   │   │   ├── MedicalRecordModal.tsx# Medical record CRUD modal
│   │   │   └── PrescriptionPanel.tsx # Prescription management panel
│   │   ├── billing/                  # Billing components
│   │   │   ├── CreateBillModal.tsx   # Bill creation modal
│   │   │   └── PaymentModal.tsx      # Payment recording modal
│   │   ├── rooms/                    # Room components
│   │   │   └── AdmitPatientModal.tsx # Patient admission modal
│   │   ├── ui/                       # Reusable UI components
│   │   │   └── index.tsx             # Modal, Button, Input, Stat Card, Status Badge, etc.
│   │   └── ErrorBoundary.tsx         # Error boundary wrapper
│   ├── lib/                          # Utility functions & API client
│   │   ├── api.ts                    # API client with all endpoint methods
│   │   └── utils.ts                  # Helper functions (formatting, date, etc.)
│   ├── hooks/                        # Custom React hooks
│   │   ├── useData.ts                # Data fetching hook
│   │   ├── useAsync.ts               # Async operations hook
│   │   ├── useValidation.ts          # Form validation hook
│   │   └── index.ts                  # Hook exports
│   ├── types/                        # TypeScript type definitions
│   │   └── index.ts                  # API types and interfaces
│   ├── tailwind.config.js            # Tailwind CSS configuration
│   ├── tsconfig.json                 # TypeScript configuration
│   ├── next.config.js                # Next.js configuration
│   ├── postcss.config.js             # PostCSS configuration
│   └── package.json                  # Frontend dependencies
│
├── database/
│   └── schema.sql                    # Database schema with tables, indexes, triggers, views
│
├── tests/                            # Pytest test suite
│   ├── conftest.py                   # Pytest configuration & fixtures
│   ├── test_patients.py              # Patient endpoint tests
│   ├── test_doctors.py               # Doctor endpoint tests
│   ├── test_appointments.py          # Appointment endpoint tests
│   ├── test_medical_records.py       # Medical record endpoint tests
│   ├── test_medicines.py             # Medicine endpoint tests
│   ├── test_rooms.py                 # Room & admission endpoint tests
│   └── test_billing.py               # Billing endpoint tests
│
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore rules
├── pyproject.toml                    # Python project configuration
├── pytest.ini                        # Pytest configuration
├── uv.lock                           # Dependency lock file
└── README.md                         # This file
```

### Architecture Highlights
- **Separation of Concerns** — API routes → Services → Repositories → Database
- **Error Handling** — Global middleware with custom exception types and consistent error responses
- **Logging** — Structured logging with color-coded output for better debugging
- **Type Safety** — Full TypeScript frontend + Pydantic-validated backend schemas
- **Scalability** — Pagination, filtering, and efficient database queries with proper indexes

## Database Schema

The system uses a normalized relational database with the following core tables:

- **patients** — Patient demographics and contact information
- **doctors** — Doctor profiles with specialization and fees
- **departments** — Hospital departments and organizational structure
- **appointments** — Appointment bookings and history
- **medical_records** — Patient medical history and diagnoses
- **medicines** — Medicine inventory and pricing
- **prescriptions** — Medicine prescriptions linked to medical records
- **rooms** — Hospital rooms with capacity and types (General, Private, ICU, Emergency)
- **admissions** — Patient room admissions and lengths of stay
- **bills** — Billing records with itemized charges

### Key Relationships
- Appointments link patients to doctors
- Medical records capture consultations and diagnoses
- Prescriptions link medical records to medicines
- Admissions manage room occupancy and patient care
- Bills aggregate charges from multiple sources

## Development & Testing

### Run Tests
```bash
uv run pytest tests/ -v
```

### Run Specific Test File
```bash
uv run pytest tests/test_patients.py -v
```

### Run with Coverage
```bash
uv run pytest tests/ --cov=backend --cov-report=html
```

## Dashboard & Frontend Features

### Dashboard Overview (`/`)
The main dashboard provides at-a-glance insights into hospital operations:

**Statistics Cards**
- Total Patients — Overall patient count
- Doctors — Active doctors with availability status
- Today's Appointments — Appointments scheduled for today
- Available Rooms — Vacant rooms with occupancy status
- Pending Bills — Bills awaiting payment
- Revenue — Total collected payments (KPI)

**Quick Actions**
- New Patient registration
- Book Appointment
- Create Medical Record
- Admit Patient
- Create Bill

**Recent Activity Sections**
- Recent Appointments — Last 6 appointments with status
- Active Admissions — Current patient admissions with room details

### Page-by-Page Overview

**Patients** (`/patients`)
- List all patients with pagination
- Search by name or phone
- Create new patient
- Edit patient details
- View patient detail page with complete history
- Access related appointments, medical records, and bills

**Patient Detail** (`/patients/[id]`)
- Patient demographics
- All appointments (with status filtering)
- Complete medical record history
- All bills related to patient
- Quick edit button

**Doctors** (`/doctors`)
- List all doctors
- View specialization and fees
- Toggle doctor availability
- Create/edit doctor profiles
- View doctor statistics

**Appointments** (`/appointments`)
- List all appointments with status
- Filter by status (Scheduled, Completed, Cancelled, No-Show)
- Search by patient name
- Create new appointment
- Update appointment details
- Cancel with notes
- Conflict detection on booking

**Medical Records** (`/medical-records`)
- List all medical records
- Filter by status
- Create new record
- View diagnosis and treatment details
- Manage prescriptions per record
- Link to appointments

**Medicines** (`/medicines`)
- Inventory dashboard
- Search medicines
- Track stock levels
- Low-stock alerts
- Create/update medicines
- Restock operations
- Expiry date tracking

**Rooms & Admissions** (`/rooms`)
- Room status and occupancy
- Filter by room type (General, Private, ICU, Emergency)
- Available rooms view
- Admission management
- Discharge workflow
- Occupancy statistics
- Room management (create/edit)

**Billing** (`/billing`)
- View all bills with status
- Filter by payment status (Pending, Paid, Partially Paid, Cancelled)
- Search by patient name
- Payment recording interface
- Bill summary statistics:
  - Total Collected
  - Outstanding Amount
  - Pending Bills
- Auto-bill generation from admissions

### UI Components
All pages share common, reusable components:

**Navigation**
- Sidebar — Fixed navigation with all modules
- Topbar — Page title, notifications, user menu
- Breadcrumbs (on detail pages)

**Layout Components**
- Card containers with shadow/border
- Responsive grid layouts
- Modal dialogs for CRUD operations
- Tables with hover effects

**Form Elements**
- Text inputs with validation
- Dropdowns/select fields
- Date/time pickers
- Currency inputs
- Text areas for notes

**Feedback Components**
- Error banners with error messages
- Loading skeletons/spinners
- Status badges (color-coded)
- Confirmation dialogs for destructive actions
- Toast-like notifications

**Data Display**
- Stat cards with icons and colors
- Tables with sorting and filtering
- Empty states with helpful messages
- Pagination controls

### Responsive Design
- Mobile-friendly on small screens (<640px)
- Tablet optimizations (640px-1024px)
- Full layout on desktop (>1024px)
- Touch-friendly buttons and inputs
- Sidebar collapses on mobile

### State Management
- React hooks (useState, useEffect) for local state
- Custom hooks for common patterns:
  - `useData()` — Data fetching with loading/error
  - `useAsync()` — Async operations with loading state
  - `useValidation()` — Form validation
- API client (`lib/api.ts`) for all backend calls

## API Usage Examples

### Patient Management
```bash
# Create a new patient
curl -X POST http://localhost:8000/patients \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "gender": "Male",
    "blood_group": "O+",
    "phone": "1234567890",
    "email": "john@example.com",
    "address": "123 Main St",
    "emergency_contact": "9876543210"
  }'

# Search patients by name or phone
curl http://localhost:8000/patients?search=John

# Get patient with all related data
curl http://localhost:8000/patients/1

# Get patient appointments
curl http://localhost:8000/patients/1/appointments

# Get patient medical records
curl http://localhost:8000/patients/1/medical-records

# Get patient bills
curl http://localhost:8000/patients/1/bills

# Get patient statistics
curl http://localhost:8000/patients/stats
```

### Appointment Management
```bash
# Create appointment
curl -X POST http://localhost:8000/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "doctor_id": 1,
    "appointment_date": "2024-04-01",
    "appointment_time": "10:00:00",
    "reason": "Regular checkup"
  }'

# Get appointments for a patient
curl http://localhost:8000/appointments/patient/1

# Get appointments for a doctor
curl http://localhost:8000/appointments/doctor/1

# Cancel appointment
curl -X PUT http://localhost:8000/appointments/1/cancel \
  -H "Content-Type: application/json" \
  -d '{"status": "Cancelled", "notes": "Patient requested cancellation"}'
```

### Medical Records & Prescriptions
```bash
# Create medical record
curl -X POST http://localhost:8000/medical-records \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "doctor_id": 1,
    "appointment_id": 1,
    "diagnosis": "Hypertension",
    "symptoms": "Elevated blood pressure",
    "treatment": "Prescribed medication",
    "notes": "Follow-up in 2 weeks"
  }'

# Add prescription to medical record
curl -X POST http://localhost:8000/medical-records/1/prescriptions \
  -H "Content-Type: application/json" \
  -d '{
    "medicine_id": 5,
    "dosage": "500mg",
    "frequency": "Twice daily",
    "duration": "30 days",
    "quantity": 60,
    "instructions": "Take with food"
  }'

# Get prescriptions for a medical record
curl http://localhost:8000/medical-records/1/prescriptions
```

### Billing & Payments
```bash
# Create bill for admission
curl -X POST http://localhost:8000/billing/admission/1/generate \
  -H "Content-Type: application/json"

# Get patient bills
curl http://localhost:8000/billing/patient/1

# Record payment
curl -X POST http://localhost:8000/billing/1/record-payment \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500,
    "payment_method": "Card",
    "description": "Partial payment"
  }'

# Get billing statistics
curl http://localhost:8000/billing/stats/billing
```

### Inventory Management
```bash
# Get low-stock medicines
curl http://localhost:8000/medicines/low-stock

# Get inventory statistics
curl http://localhost:8000/medicines/stats/inventory

# Restock medicine
curl -X POST http://localhost:8000/medicines/1/restock \
  -H "Content-Type: application/json" \
  -d '{"quantity": 100}'
```

### Room & Admission Management
```bash
# List available rooms
curl http://localhost:8000/rooms/available

# Get rooms by type
curl http://localhost:8000/rooms/by-type/ICU

# Admit patient
curl -X POST http://localhost:8000/admissions \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "room_id": 5,
    "doctor_id": 1,
    "reason": "Post-operative recovery"
  }'

# Get active admissions
curl http://localhost:8000/admissions/active

# Discharge patient
curl -X POST http://localhost:8000/admissions/1/discharge \
  -H "Content-Type: application/json" \
  -d '{"discharge_notes": "Patient recovered well"}'

# Get occupancy statistics
curl http://localhost:8000/rooms/occupancy/stats
```

## Implementation Status

### ✅ Fully Implemented Features
- ✅ Complete CRUD operations for all resources
- ✅ Advanced search (patients by name/phone)
- ✅ Pagination with skip/limit parameters
- ✅ Relationship queries (patient appointments, records, bills)
- ✅ Appointment conflict detection and status management
- ✅ Medical records with prescription management
- ✅ Bill generation and automatic calculation from admissions
- ✅ Payment recording and status tracking
- ✅ Medicine inventory with low-stock alerts
- ✅ Room occupancy management
- ✅ Patient admission and discharge workflow
- ✅ Doctor availability toggle
- ✅ Statistics endpoints (patients, billing, inventory, admissions, occupancy)
- ✅ Dashboard UI with statistics and quick actions
- ✅ Responsive frontend with modal-based operations
- ✅ Error boundaries and loading states
- ✅ API documentation (Swagger & ReDoc)
- ✅ Service layer with business logic separation
- ✅ Repository pattern for data access
- ✅ Custom exception handling with middleware
- ✅ Structured logging with color support
- ✅ Comprehensive test suite

### 🔄 In Progress/Refactoring
- Optimizing router performance with refactored versions
- Enhanced endpoint standardization

## Known Limitations & Future Enhancements

### Current Limitations
- ⚠️ **No Authentication** — All endpoints are public (no JWT/auth system)
- ⚠️ **No Authorization** — No user roles or permissions system
- ⚠️ **No Audit Logging** — No tracking of who made what changes
- ⚠️ **No File Support** — No document/image upload capabilities
- ⚠️ **Departments** — Departments table exists but has no API endpoints
- ⚠️ **No Real-time Updates** — No WebSocket support for live data

### Roadmap for Future Enhancements
- 🔐 JWT authentication and role-based access control (Admin, Doctor, Receptionist, Patient)
- 📊 Advanced reporting with exportable PDFs and charts
- 📱 Mobile app (React Native) with offline support
- 📄 Document management (medical reports, prescriptions, discharge summaries)
- 🔔 Real-time notifications (email, SMS, in-app)
- 📨 Email integration for automated appointment reminders
- 🧮 Advanced billing reports, insurance claim generation
- 📈 Performance analytics and KPI dashboards
- 🔄 Audit logging for compliance and accountability
- 🌐 Multi-language support
- 📍 Telemedicine capabilities

## Troubleshooting

### Backend Issues

**Module not found errors:**
```bash
# Reinstall dependencies
uv sync
uv pip list  # Verify installation
```

**Database connection errors:**
```bash
# Check if MariaDB/MySQL is running
sudo systemctl status mariadb  # Ubuntu/Debian
brew services list | grep mysql  # macOS

# Start MariaDB if not running
sudo systemctl start mariadb  # Ubuntu/Debian
brew services start mariadb  # macOS

# Verify credentials and database
mariadb -u root -p -e "SHOW DATABASES;"
mariadb -u root -p hospital_management -e "SHOW TABLES;"
```

**Port already in use (8000):**
```bash
# Find and kill process using port 8000
lsof -i :8000
kill -9 <PID>
# Or use a different port
uv run uvicorn backend.main:app --port 8001 --reload
```

**Pydantic validation errors:**
- Check request body matches schema definitions
- Verify all required fields are provided
- Check data types (especially date/time formats)

**Import errors:**
```bash
# Ensure you're in the correct directory and environment
cd "/home/kernel00/Codes/Hospital Management System"
source .venv/bin/activate  # or use uv run
```

### Frontend Issues

**npm dependencies issues:**
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install

# Or use alternative
npm ci  # Clean install from package-lock.json
```

**API connection errors:**
- Check `NEXT_PUBLIC_API_URL` in `.env.local` (default: `http://localhost:8000`)
- Ensure backend is running and accessible
- Check browser console for CORS errors
- Verify backend health: `curl http://localhost:8000/health`

**Port already in use (3000):**
```bash
# Find and kill process
lsof -i :3000
kill -9 <PID>
# Or use different port
npm run dev -- -p 3001
```

**Build errors:**
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

**Type errors:**
```bash
# Regenerate types if API changed
npm run lint  # Check for TypeScript errors
```

### Database Issues

**Foreign key constraint errors:**
- Ensure referenced records exist before creating relationships
- Check data integrity with: `mariadb -u root -p hospital_management < database/schema.sql`

**Trigger or stored procedure errors:**
- Verify triggers were created: `SHOW TRIGGERS;`
- Check trigger syntax: `SHOW CREATE TRIGGER trigger_name;`

**Data inconsistency:**
```bash
# Run recalculation script
uv run python backend/scripts/recalculate_bills.py
```

### Performance Issues

**Slow queries:**
- Check indexes: `SHOW INDEX FROM table_name;`
- Use pagination: `?skip=0&limit=50`
- Monitor query performance with `EXPLAIN`

**High memory usage:**
- Reduce pagination limit in requests
- Enable query caching
- Consider database optimization

### CORS Issues

If you see CORS errors in the browser:
1. Verify `CORS_ORIGINS` in `.env` includes your frontend URL
2. Check `CORS_METHODS` and `CORS_HEADERS` are set correctly
3. Ensure backend is accessible from frontend URL
4. Clear browser cache and try again

Default CORS settings allow:
- Origins: `http://localhost:3000`, `http://localhost:8000`
- Methods: GET, POST, PUT, DELETE, PATCH, OPTIONS
- Headers: All

## Performance Considerations

- Database queries use indexes on frequently searched fields (patient name, phone, doctor specialization)
- API endpoints support pagination with `skip` and `limit` parameters
- Frontend uses custom hooks for efficient data fetching and caching
- Components are lazy-loaded for optimal performance

## Security Notes & Production Deployment

⚠️ **IMPORTANT:** This system currently has **NO AUTHENTICATION** and **NO AUTHORIZATION**. Before deploying to production:

### Critical Security Tasks
1. **Authentication & Authorization**
   - Implement JWT authentication
   - Add user roles (Admin, Doctor, Receptionist, Patient)
   - Implement role-based access control (RBAC)
   - Secure password hashing (bcrypt, argon2)

2. **Data Protection**
   - Enable HTTPS/TLS with valid certificates
   - Implement rate limiting to prevent brute-force attacks
   - Add input validation and sanitization
   - Use parameterized queries (already using SQLAlchemy)
   - Encrypt sensitive data (passwords, SSN, medical data at rest)

3. **API Security**
   - Add request signing
   - Implement API versioning
   - Add request size limits
   - Enable CORS only for trusted origins
   - Add request timeout limits

4. **Database Security**
   - Use strong passwords for database users
   - Restrict database access by IP/firewall
   - Enable database audit logging
   - Regular backups with encryption
   - Use connection pooling
   - Implement row-level security for multi-tenant support

5. **Application Monitoring**
   - Implement comprehensive logging and monitoring
   - Set up alerts for suspicious activities
   - Regular security audits and penetration testing
   - Health checks and uptime monitoring
   - Error tracking (Sentry, etc.)

6. **Patient Data Privacy (HIPAA/GDPR)**
   - Implement audit trails for data access
   - Add data retention policies
   - Anonymization for analytics
   - Patient consent management
   - Data export capabilities for GDPR compliance

### Environment Configuration for Production
```env
# .env.production
ENVIRONMENT=production
DEBUG=false

# Use strong, unique values
SECRET_KEY=generate-with-secrets.token_urlsafe(32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# Database with SSL
DB_HOST=production-db.example.com
DB_PORT=3306
DB_USER=app_user_prod
DB_PASSWORD=strong-random-password
DB_NAME=hospital_management_prod
DB_ECHO=false

# CORS - only trusted origins
CORS_ORIGINS=["https://your-domain.com"]
CORS_CREDENTIALS=true

# Logging
LOG_LEVEL=INFO
```

### Deployment Checklist
- [ ] Enable HTTPS/SSL certificates
- [ ] Change all default credentials
- [ ] Enable authentication on all endpoints
- [ ] Set up database backups
- [ ] Configure logging and monitoring
- [ ] Set up alerts and notifications
- [ ] Implement rate limiting
- [ ] Enable CORS for allowed origins only
- [ ] Run security audit
- [ ] Test disaster recovery procedures
- [ ] Document security policies
- [ ] Set up incident response procedures

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write Tests** for any new functionality
   ```bash
   uv run pytest tests/test_your_feature.py -v
   ```

3. **Follow Code Style**
   - Backend: PEP 8 with type hints
   - Frontend: ESLint rules + Prettier formatting
   - Use meaningful variable/function names
   - Add docstrings to functions and classes

4. **Ensure All Tests Pass**
   ```bash
   uv run pytest tests/ -v
   npm run lint  # Frontend
   ```

5. **Create Pull Request** with clear description
   - Explain what problem it solves
   - Link any related issues
   - Add screenshots for UI changes

## FAQ

**Q: Can I run this on Windows?**  
A: Yes, install WSL2 (Windows Subsystem for Linux) or use Docker. Native Windows support requires adjusting terminal commands.

**Q: How do I update dependencies?**  
A: Run `uv pip install --upgrade <package>` for Python or `npm update` for Node packages.

**Q: Can I modify the database schema?**  
A: Yes, update `database/schema.sql`, then reimport it. Create a migration if needed for production.

**Q: How do I backup the database?**  
```bash
mysqldump -u root -p hospital_management > backup.sql
# Restore from backup
mysql -u root -p hospital_management < backup.sql
```

**Q: Can I use PostgreSQL instead of MySQL?**  
A: The system uses SQLAlchemy, so it's possible with dialect changes, but the schema would need conversion.

**Q: How do I scale this to production?**  
A: 
- Use Docker containers for both backend and frontend
- Set up a reverse proxy (nginx)
- Use a managed database service
- Implement caching (Redis)
- Set up monitoring and logging
- Enable authentication and HTTPS

## License

MIT License - This project is open source and free to use, modify, and distribute.

## Support & Contact

For issues, feature requests, or questions:
- **GitHub Issues** — Report bugs or request features
- **Documentation** — Check README sections and `/docs` API endpoint
- **API Docs** — Visit `http://localhost:8000/docs` (when running) for Swagger UI
- **ReDoc** — Visit `http://localhost:8000/redoc` for ReDoc documentation

## Related Information

- **Author** — Arun Aryal
- **Version** — 1.0.0
- **Last Updated** — March 25, 2026
- **Repository** — [GitHub](https://github.com/ArunAryal/HospitalManagementSystem)
- **Status** — Active Development

## Acknowledgments

This project uses:
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [SQLAlchemy](https://www.sqlalchemy.org/) for ORM
- [Pydantic](https://docs.pydantic.dev/) for data validation
- [Next.js](https://nextjs.org/) for the frontend framework
- [Tailwind CSS](https://tailwindcss.com/) for styling
- [MariaDB/MySQL](https://mariadb.org/) for the database

---

**Made with ❤️ for better hospital management**