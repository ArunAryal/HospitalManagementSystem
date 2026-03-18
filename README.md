# 🏥 Hospital Management System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

A comprehensive, production-ready Hospital Management System built with **FastAPI** and **MySQL**, featuring advanced database concepts including triggers, stored procedures, and views.

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [API Docs](#-api-documentation) • [Tech Stack](#-tech-stack) • [Database Schema](#-database-schema)

</div>

---

## 📋 Table of Contents

- [About](#-about-the-project)
- [Features](#-features)
- [Demo](#-demo)
- [Tech Stack](#-tech-stack)
- [Database Schema](#-database-schema)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Advanced Database Features](#-advanced-database-features)
- [Screenshots](#-screenshots)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)
- [Acknowledgments](#-acknowledgments)

---

## 🎯 About The Project

The Hospital Management System is a full-stack web application designed to streamline hospital operations including patient management, doctor scheduling, appointment booking and medical records.This project demonstrates advanced database management concepts and modern web development practices.

### Built With

- **Backend Framework:** FastAPI (Python)
- **Database:** MySQL 8.0
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **API Documentation:** Swagger/OpenAPI

---

## ✨ Features

### Core Modules

- 🏥 **Patient Management**
  - Complete patient registration and profile management
  - Medical history tracking
  - Emergency contact information

- 👨‍⚕️ **Doctor Management**
  - Doctor profiles with specializations
  - Qualification and experience tracking
  - Availability status management

- 📅 **Appointment System**
  - Real-time appointment booking
  - Conflict detection and prevention
  - Status tracking (Scheduled, Completed, Cancelled, No-Show)
  - Today's appointments dashboard

- 📝 **Medical Records**
  - Diagnosis and treatment documentation
  - Prescription management
  - Patient history tracking

### Technical Features

- ✅ **RESTful API** with multiple endpoints
- ✅ **Interactive API Documentation** (Swagger UI)
- ✅ **Stored Procedures** for complex calculations
- ✅ **Database Views** for reporting
- ✅ **Foreign Key Constraints** for data integrity
- ✅ **Input Validation** using Pydantic schemas
- ✅ **CORS Support** for frontend integration
- ✅ **Responsive UI** with Bootstrap 5

---

## 🎬 Demo

### Dashboard

The main dashboard provides an overview of key metrics and quick access to common tasks.

### API Documentation

Interactive API documentation available at `/docs` endpoint with Swagger UI.

**Live Demo:** Coming Soon!  
**API Docs:** `http://localhost:8000/docs` (when running locally)

---

## 🛠️ Tech Stack

### Backend

| Technology    | Purpose                         |
| ------------- | ------------------------------- |
| FastAPI       | Modern Python web framework     |
| SQLAlchemy    | SQL toolkit and ORM             |
| Pydantic      | Data validation and settings    |
| PyMySQL       | MySQL database driver           |
| Uvicorn       | ASGI web server                 |
| Python-dotenv | Environment variable management |

### Frontend

| Technology  | Purpose       |
| ----------- | ------------- |
| HTML5       | Structure     |
| CSS3        | Styling       |
| JavaScript  | Interactivity |
| Bootstrap 5 | UI Framework  |
| Fetch API   | HTTP requests |

### Database

- **MySQL 8.0** - Primary database
- **11 Tables** with normalized schema (3NF)
- **3 Triggers** for automation
- **1 Stored Procedure** for billing
- **4 Views** for reporting

---

## 🗄️ Database Schema

### Tables Overview

```
patients          → Patient information
doctors           → Doctor profiles and specializations
appointments      → Appointment scheduling
medical_records   → Patient diagnoses and treatments
prescriptions     → Medicine prescriptions
admissions        → Patient admissions
departments       → Hospital departments
staff             → Hospital staff members
```

### Key Relationships

- **One-to-Many**: Patient → Appointments, Doctor → Appointments
- **Many-to-Many**: Patients ↔ Medicines (through Prescriptions)
- **Foreign Keys**: 15+ relationships ensuring referential integrity

<!-- ### ER Diagram-->

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### Step-by-Step Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/hospital-management-system.git
   cd hospital-management-system
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Setup MySQL Database**

   ```bash
   # Login to MySQL
   mysql -u root -p

   # Import the schema
   source database/schema.sql

   # Or use command line
   mysql -u root -p < database/schema.sql
   ```

4. **Configure Environment Variables**

   ```bash
   # Edit the .env file
   nano .env
   ```

   Update with your MySQL credentials:

   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=hospital_management
   ```

5. **Run the Backend Server**

   ```bash
   cd backend
   python main.py
   ```

   The API will be available at:
   - Main API: `http://localhost:8000`
   - Interactive Docs: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

6. **Run the Frontend**

   ```bash
   cd frontend
   python -m http.server 8080
   ```

   Open your browser and navigate to: `http://localhost:8080`

---

## 💻 Usage

### Quick Start

1. **Access the Dashboard**
   - Navigate to `http://localhost:8080`
   - View statistics and today's appointments

2. **Add a Doctor**
   - Go to "Doctors" page
   - Click "Add New Doctor"
   - Fill in required information
   - Email must be unique

3. **Register a Patient**
   - Go to "Patients" page
   - Click "Add New Patient"
   - Complete the registration form

4. **Book an Appointment**
   - Go to "Appointments" page
   - Select patient and doctor
   - Choose date and time
   - System prevents booking conflicts

### Sample Data

The database comes pre-loaded with:

- 3 Sample Doctors (Cardiology, Pediatrics, Orthopedics)
- 3 Sample Medicines (Paracetamol, Amoxicillin, Ibuprofen)

---

## 📚 API Documentation

### Base URL

```
http://localhost:8000
```

### Main Endpoints

#### Patients

- `GET /patients` - Get all patients
- `POST /patients` - Create new patient
- `GET /patients/{id}` - Get patient by ID
- `PUT /patients/{id}` - Update patient
- `DELETE /patients/{id}` - Delete patient
- `GET /patients/{id}/appointments` - Get patient's appointments
- `GET /patients/{id}/medical-records` - Get patient's medical records

#### Doctors

- `GET /doctors` - Get all doctors
- `POST /doctors` - Create new doctor
- `GET /doctors/{id}` - Get doctor by ID
- `PUT /doctors/{id}` - Update doctor
- `DELETE /doctors/{id}` - Delete doctor
- `GET /doctors?specialization={spec}` - Filter by specialization

#### Appointments

- `GET /appointments` - Get all appointments
- `POST /appointments` - Create appointment
- `GET /appointments/{id}` - Get appointment by ID
- `PUT /appointments/{id}` - Update appointment
- `DELETE /appointments/{id}` - Delete appointment
- `GET /appointments/today/list` - Get today's appointments

#### Medical Records

- `GET /medical-records` - Get all records
- `POST /medical-records` - Create medical record
- `GET /medical-records/{id}` - Get record by ID
- `PUT /medical-records/{id}` - Update record
- `DELETE /medical-records/{id}` - Delete record

#### Medicines

- `GET /medicines` - Get all medicines
- `POST /medicines` - Add new medicine
- `GET /medicines/{id}` - Get medicine by ID
- `PUT /medicines/{id}` - Update medicine
- `DELETE /medicines/{id}` - Delete medicine
- `GET /medicines/low-stock/list` - Get low-stock medicines
- `POST /medicines/{id}/restock?quantity={qty}` - Restock medicine


### Example Requests

**Create a Patient:**

```bash
curl -X POST "http://localhost:8000/patients" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "gender": "Male",
    "phone": "1234567890",
    "blood_group": "A+",
    "email": "john.doe@example.com"
  }'
```

**Book an Appointment:**

```bash
curl -X POST "http://localhost:8000/appointments" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "doctor_id": 1,
    "appointment_date": "2024-03-15",
    "appointment_time": "10:00:00",
    "reason": "Regular checkup"
  }'
```

For complete API documentation with all request/response schemas, visit the Swagger UI at `http://localhost:8000/docs` when the server is running.

---

## 📁 Project Structure

```
hospital-management-system/
├── backend/
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── patients.py
│   │   ├── doctors.py
│   │   ├── appointments.py
│   │   ├── medical_records.py
│   │   ├── medicines.py
│   │   └── billing.py
│   ├── __init__.py
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   └── main.py              # FastAPI application
├── frontend/
│   ├── assets/
│   │   ├── css/
│   │   └── js/
│   │       ├── config.js
│   │       └── dashboard.js
│   ├── index.html           # Dashboard
│   ├── patients.html        # Patient management
│   ├── doctors.html         # Doctor management
│   ├── appointments.html    # Appointment booking
│   ├── medicines.html       # Medicine inventory
│   └── billing.html         # Billing management
├── database/
│   └── schema.sql           # Complete database schema
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── QUICKSTART.md           # Quick setup guide
└── PROJECT_SUMMARY.md      # Project overview
```

---

## 🎯 Advanced Database Features

### Triggers

1. **after_admission_insert** - Automatically updates room occupancy when a patient is admitted
2. **after_admission_update** - Updates room occupancy when a patient is discharged
3. **after_prescription_insert** - Reduces medicine stock when prescriptions are created

### Stored Procedures

### Views

1. **patient_appointment_history** - Complete appointment history with patient and doctor details
2. **doctor_schedule** - Upcoming appointments for all doctors
3. **low_stock_medicines** - Medicines below reorder level
4. **room_availability** - Current room occupancy status

### Indexes

Strategic indexes on:

- Patient name and phone
- Doctor specialization
- Appointment date and status
- Medicine name
- And more for optimal query performance

---

## 📸 Screenshots

### Dashboard

![Dashboard](screenshots/dashboard.png)
_Main dashboard with statistics and quick actions_

### Patient Management

![Patients](screenshots/patients.png)
_Patient registration and management interface_

### Appointment Booking

![Appointments](screenshots/appointments.png)
_Appointment scheduling with conflict detection_

### API Documentation

![API Docs](screenshots/api-docs.png)
_Interactive Swagger UI documentation_

_(Add actual screenshots to your repository in a `screenshots/` folder)_

---

## 🗺️ Roadmap

- [x] Core patient management
- [x] Doctor scheduling
- [x] Appointment system
- [x] Medical records
- [x] Medicine inventory
- [x] Billing system
- [x] Room management
- [ ] User authentication & authorization
- [ ] Role-based access control (Admin, Doctor, Receptionist)
- [ ] Email/SMS notifications
- [ ] Report generation (PDF/Excel)
- [ ] Analytics dashboard
- [ ] Lab test management
- [ ] Pharmacy integration
- [ ] Insurance claim processing
- [ ] Mobile app
- [ ] Real-time notifications (WebSockets)

See the [open issues](https://github.com/yourusername/hospital-management-system/issues) for a full list of proposed features and known issues.

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

### How to Contribute

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines

- Write clean, maintainable code
- Follow PEP 8 style guide for Python
- Add comments for complex logic
- Update documentation as needed
- Test your changes thoroughly
- Add appropriate error handling

---

## 📝 License

Distributed under the MIT License. See `LICENSE` file for more information.

---

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - your.email@example.com

Project Link: [https://github.com/yourusername/hospital-management-system](https://github.com/yourusername/hospital-management-system)

---

## 🙏 Acknowledgments

This project was developed as part of a Database Management Systems course project.

### Resources Used

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Bootstrap 5](https://getbootstrap.com/)
- [Bootstrap Icons](https://icons.getbootstrap.com/)

---

<div align="center">

### ⭐ Star this repository if you find it helpful!

Made with ❤️ by [@ArunAryal]

</div>
