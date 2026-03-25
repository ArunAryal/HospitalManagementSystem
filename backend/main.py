from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import patients, doctors, appointments, medical_records, billing, medicines, rooms

app = FastAPI(
    title="Hospital Management System API",
    description="A comprehensive Hospital Management System with patient, doctor, appointment, and billing management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(medical_records.router)
app.include_router(billing.router)
app.include_router(medicines.router)
app.include_router(rooms.router)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Hospital Management System API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)