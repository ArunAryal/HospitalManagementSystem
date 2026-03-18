// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// API Endpoints
const API_ENDPOINTS = {
    patients: `${API_BASE_URL}/patients`,
    doctors: `${API_BASE_URL}/doctors`,
    appointments: `${API_BASE_URL}/appointments`,
    medicalRecords: `${API_BASE_URL}/medical-records`,
    todayAppointments: `${API_BASE_URL}/appointments/today/list`,
};

// Utility function to make API calls
async function apiCall(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'An error occurred');
        }

        if (method === 'DELETE') {
            return { success: true };
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}
