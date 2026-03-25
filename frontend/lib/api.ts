const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    
    // Handle Pydantic validation errors (array of errors)
    if (Array.isArray(err.detail)) {
      const messages = err.detail.map((e: any) => 
        `${e.loc?.[1] || 'Field'}: ${e.msg}`
      ).join('; ');
      throw new Error(messages || 'Validation error');
    }
    
    // Handle regular error messages (string)
    throw new Error(
      (typeof err.detail === 'string' ? err.detail : null) || 
      err.message || 
      'Request failed'
    );
  }
  if (res.status === 204) return null as any;
  return res.json();
}

// ─── Patients ────────────────────────────────────────────────────────────────
export const patientsApi = {
  list: (skip = 0, limit = 100) =>
    request<any[]>(`/patients/?skip=${skip}&limit=${limit}`),
  search: (query: string, skip = 0, limit = 100) =>
    request<any[]>(`/patients/?search=${encodeURIComponent(query)}&skip=${skip}&limit=${limit}`),
  get: (id: number) => request<any>(`/patients/${id}`),
  getWithDoctor: (id: number) => request<any>(`/patients/${id}/with-doctor`),
  create: (data: any) =>
    request<any>('/patients/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: any) =>
    request<any>(`/patients/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: number) =>
    request<any>(`/patients/${id}`, { method: 'DELETE' }),
  appointments: (id: number) => request<any[]>(`/patients/${id}/appointments`),
  records: (id: number) => request<any[]>(`/patients/${id}/medical-records`),
  bills: (id: number) => request<any[]>(`/patients/${id}/bills`),
};

// ─── Doctors ─────────────────────────────────────────────────────────────────
export const doctorsApi = {
  list: (skip = 0, limit = 100) =>
    request<any[]>(`/doctors/?skip=${skip}&limit=${limit}`),
  get: (id: number) => request<any>(`/doctors/${id}`),
  create: (data: any) =>
    request<any>('/doctors/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: any) =>
    request<any>(`/doctors/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: number) =>
    request<any>(`/doctors/${id}`, { method: 'DELETE' }),
  appointments: (id: number) => request<any[]>(`/doctors/${id}/appointments`),
};

// ─── Appointments ─────────────────────────────────────────────────────────────
export const appointmentsApi = {
  list: (skip = 0, limit = 100) =>
    request<any[]>(`/appointments/?skip=${skip}&limit=${limit}`),
  get: (id: number) => request<any>(`/appointments/${id}`),
  create: (data: any) =>
    request<any>('/appointments/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: any) =>
    request<any>(`/appointments/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  updateStatus: (id: number, status: string) =>
    request<any>(`/appointments/${id}`, { 
      method: 'PUT', 
      body: JSON.stringify({ status }) 
    }),
  delete: (id: number) =>
    request<any>(`/appointments/${id}`, { method: 'DELETE' }),
};

// ─── Medical Records ──────────────────────────────────────────────────────────
export const medicalRecordsApi = {
  list: (skip = 0, limit = 100) =>
    request<any[]>(`/medical-records/?skip=${skip}&limit=${limit}`),
  get: (id: number) => request<any>(`/medical-records/${id}`),
  create: (data: any) =>
    request<any>('/medical-records/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: any) =>
    request<any>(`/medical-records/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: number) =>
    request<any>(`/medical-records/${id}`, { method: 'DELETE' }),
  prescriptions: (id: number) => request<any[]>(`/medical-records/${id}/prescriptions`),
  addPrescription: (recordId: number, data: any) =>
    request<any>(`/medical-records/${recordId}/prescriptions/`, { method: 'POST', body: JSON.stringify(data) }),
};

// ─── Medicines ────────────────────────────────────────────────────────────────
export const medicinesApi = {
  list: (skip = 0, limit = 100) =>
    request<any[]>(`/medicines/?skip=${skip}&limit=${limit}`),
  get: (id: number) => request<any>(`/medicines/${id}`),
  create: (data: any) =>
    request<any>('/medicines/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: any) =>
    request<any>(`/medicines/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: number) =>
    request<any>(`/medicines/${id}`, { method: 'DELETE' }),
};

// ─── Billing ─────────────────────────────────────────────────────────────────
export const billingApi = {
  listBills: (skip = 0, limit = 100) =>
    request<any[]>(`/bills/?skip=${skip}&limit=${limit}`),
  getBill: (id: number) => request<any>(`/bills/${id}`),
  createBill: (data: any) =>
    request<any>('/bills/', { method: 'POST', body: JSON.stringify(data) }),
  updateBill: (id: number, data: any) =>
    request<any>(`/bills/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  listRooms: (skip = 0, limit = 100) =>
    request<any[]>(`/rooms/?skip=${skip}&limit=${limit}`),
  getRoom: (id: number) => request<any>(`/rooms/${id}`),
  createRoom: (data: any) =>
    request<any>('/rooms/', { method: 'POST', body: JSON.stringify(data) }),
  updateRoom: (id: number, data: any) =>
    request<any>(`/rooms/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  listAdmissions: (skip = 0, limit = 100) =>
    request<any[]>(`/admissions/?skip=${skip}&limit=${limit}`),
  createAdmission: (data: any) =>
    request<any>('/admissions/', { method: 'POST', body: JSON.stringify(data) }),
  discharge: (id: number, data: any) =>
    request<any>(`/admissions/${id}/discharge`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
};
