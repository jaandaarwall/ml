const API_BASE_URL = 'http://localhost:5000/api'

const apiCall = async (endpoint, options = {}) => {
  const authToken = localStorage.getItem('authToken')
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  }

  if (authToken) {
    headers['Authentication-Token'] = authToken
  }

  const config = {
    ...options,
    headers
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.message || 'API Error')
  }

  return await response.json()
}

export const authAPI = {
  login: (email, password) => 
    apiCall('/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    }),

  register: (username, email, password) => 
    apiCall('/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password })
    }),

  logout: () => 
    apiCall('/logout', { method: 'POST' }),

  checkEmail: (email) => 
    apiCall('/check-email', {
      method: 'POST',
      body: JSON.stringify({ email })
    })
}

export const adminAPI = {
  getDashboard: () => apiCall('/admin/dashboard'),
  
  getDoctors: () => apiCall('/admin/doctors'),
  
  addDoctor: (data) => 
    apiCall('/admin/doctor/add', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getDoctorDetail: (doctorId) => apiCall(`/admin/doctor/${doctorId}`),
  
  updateDoctor: (doctorId, data) => 
    apiCall(`/admin/doctor/${doctorId}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }),

  deactivateDoctor: (doctorId) => 
    apiCall(`/admin/doctor/${doctorId}`, { method: 'DELETE' }),

  getPatients: () => apiCall('/admin/patients'),
  
  getPatientDetail: (patientId) => apiCall(`/admin/patient/${patientId}`),
  
  deactivatePatient: (patientId) => 
    apiCall(`/admin/patient/${patientId}`, { method: 'DELETE' }),

  getAppointments: () => apiCall('/admin/appointments'),
  
  search: (query, type = 'all') => 
    apiCall(`/admin/search?q=${query}&type=${type}`),

  getAnalytics: () => apiCall('/admin/analytics')
}

export const doctorAPI = {
  getDashboard: () => apiCall('/doctor/dashboard'),
  
  getAppointments: () => apiCall('/doctor/appointments'),
  
  getPatients: () => apiCall('/doctor/patients'),
  
  getAvailability: () => apiCall('/doctor/availability'),
  
  addAvailability: (data) => 
    apiCall('/doctor/availability', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  deleteAvailability: (availabilityId) => 
    apiCall(`/doctor/availability?id=${availabilityId}`, { method: 'DELETE' }),

  completeAppointment: (appointmentId) => 
    apiCall(`/doctor/appointment/${appointmentId}/complete`, { method: 'POST' }),

  getTreatment: (appointmentId) => 
    apiCall(`/doctor/appointment/${appointmentId}/treatment`),

  saveTreatment: (appointmentId, data) => 
    apiCall(`/doctor/appointment/${appointmentId}/treatment`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getPatientHistory: (patientId) => 
    apiCall(`/doctor/patient/${patientId}/history`),

  getProfile: () => apiCall('/doctor/profile'),
  
  updateProfile: (data) => 
    apiCall('/doctor/profile', {
      method: 'PUT',
      body: JSON.stringify(data)
    }),

  getAnalytics: () => apiCall('/doctor/analytics')
}

export const patientAPI = {
  getDashboard: () => apiCall('/patient/dashboard'),
  
  getDoctors: (departmentId = null) => {
    let url = '/patient/doctors'
    if (departmentId) url += `?department_id=${departmentId}`
    return apiCall(url)
  },

  getDoctorAvailability: (doctorId, date) => 
    apiCall(`/patient/doctor/${doctorId}/availability?date=${date}`),

  bookAppointment: (doctorId, data) => 
    apiCall(`/patient/book/${doctorId}`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getAppointments: () => apiCall('/patient/appointments'),
  
  cancelAppointment: (appointmentId) => 
    apiCall(`/patient/appointment/${appointmentId}/cancel`, { method: 'POST' }),

  getHistory: () => apiCall('/patient/history'),
  
  getProfile: () => apiCall('/patient/profile'),
  
  updateProfile: (data) => 
    apiCall('/patient/profile', {
      method: 'PUT',
      body: JSON.stringify(data)
    }),

  getAnalytics: () => apiCall('/patient/analytics')
}

export const departmentsAPI = {
  getDepartments: () => apiCall('/departments')
}

export const paymentAPI = {
  processPayment: (paymentId) => 
    apiCall(`/payment/${paymentId}/pay`, { method: 'POST' })
}