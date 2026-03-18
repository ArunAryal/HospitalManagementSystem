// Dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});

async function loadDashboardData() {
    try {
        // Load statistics
        await Promise.all([
            loadPatientCount(),
            loadDoctorCount(),
            loadTodayAppointments(),
            loadPendingBills()
        ]);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showAlert('Error loading dashboard data', 'danger');
    }
}

async function loadPatientCount() {
    try {
        const patients = await apiCall(API_ENDPOINTS.patients);
        document.getElementById('totalPatients').textContent = patients.length;
    } catch (error) {
        console.error('Error loading patient count:', error);
    }
}

async function loadDoctorCount() {
    try {
        const doctors = await apiCall(API_ENDPOINTS.doctors);
        document.getElementById('totalDoctors').textContent = doctors.length;
    } catch (error) {
        console.error('Error loading doctor count:', error);
    }
}

async function loadTodayAppointments() {
    try {
        const appointments = await apiCall(API_ENDPOINTS.todayAppointments);
        document.getElementById('todayAppointments').textContent = appointments.length;
        
        // Display appointments in table
        const tableBody = document.getElementById('todayAppointmentsTable');
        
        if (appointments.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No appointments for today</td></tr>';
            return;
        }
        
        // Fetch patient and doctor details for each appointment
        const appointmentsWithDetails = await Promise.all(
            appointments.slice(0, 5).map(async (apt) => {
                try {
                    const patient = await apiCall(`${API_ENDPOINTS.patients}/${apt.patient_id}`);
                    const doctor = await apiCall(`${API_ENDPOINTS.doctors}/${apt.doctor_id}`);
                    return {
                        ...apt,
                        patientName: `${patient.first_name} ${patient.last_name}`,
                        doctorName: `${doctor.first_name} ${doctor.last_name}`
                    };
                } catch (error) {
                    return {
                        ...apt,
                        patientName: 'Unknown',
                        doctorName: 'Unknown'
                    };
                }
            })
        );
        
        tableBody.innerHTML = appointmentsWithDetails.map(apt => `
            <tr>
                <td>${apt.appointment_id}</td>
                <td>${apt.patientName}</td>
                <td>${apt.doctorName}</td>
                <td>${apt.appointment_time}</td>
                <td><span class="badge bg-${getStatusColor(apt.status)}">${apt.status}</span></td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Error loading today appointments:', error);
        document.getElementById('todayAppointmentsTable').innerHTML = 
            '<tr><td colspan="5" class="text-center text-danger">Error loading appointments</td></tr>';
    }
}

async function loadPendingBills() {
    try {
        const bills = await apiCall(API_ENDPOINTS.pendingBills);
        document.getElementById('pendingBills').textContent = bills.length;
    } catch (error) {
        console.error('Error loading pending bills:', error);
    }
}

function getStatusColor(status) {
    const colors = {
        'Scheduled': 'primary',
        'Completed': 'success',
        'Cancelled': 'danger',
        'No-Show': 'warning'
    };
    return colors[status] || 'secondary';
}
