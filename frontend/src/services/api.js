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
    }),

  forgotPassword: (email) => 
    apiCall('/forgot-password', {
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

  getAnalytics: () => apiCall('/admin/analytics'),

  getTransactions: () => apiCall('/admin/transactions'),

  // Departments Management
  getDepartmentsManaged: () => apiCall('/admin/manage-departments'),

  addDepartment: (data) =>
    apiCall('/admin/manage-departments', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  updateDepartment: (id, data) =>
    apiCall(`/admin/department/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }),

  deleteDepartment: (id) =>
    apiCall(`/admin/department/${id}`, { method: 'DELETE' }),

  // Export Tasks
  exportAppointments: (startDate, endDate) => 
    apiCall('/task/export-admin-appointments', {
      method: 'POST',
      body: JSON.stringify({ start_date: startDate, end_date: endDate })
    }),
  
  exportTransactions: (startDate, endDate) => 
    apiCall('/task/export-admin-transactions', {
      method: 'POST',
      body: JSON.stringify({ start_date: startDate, end_date: endDate })
    }),
    
  getTaskStatus: (taskId) => 
    apiCall(`/task/status/${taskId}`)
}

export const doctorAPI = {
  getDashboard: () => apiCall('/doctor/dashboard'),
  
  getAppointments: (date = null) => {
      let url = '/doctor/appointments'
      if (date) url += `?date=${date}`
      return apiCall(url)
  },
  
  getPatients: () => apiCall('/doctor/patients'),
  
  getAvailability: () => apiCall('/doctor/availability'),
  
  addAvailability: (data) => 
    apiCall('/doctor/availability', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  deleteAvailability: (availabilityId) => 
    apiCall(`/doctor/availability?id=${availabilityId}`, { method: 'DELETE' }),
  
  deleteAvailabilitySlot: (availabilityId, time) =>
    apiCall(`/doctor/availability/${availabilityId}/slot?time=${time}`, { method: 'DELETE' }),

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

  getAnalytics: () => apiCall('/doctor/analytics'),

  // Export Task
  exportAppointments: (startDate, endDate) => 
    apiCall('/task/export-doctor-appointments', {
      method: 'POST',
      body: JSON.stringify({ start_date: startDate, end_date: endDate })
    }),
    
  getTaskStatus: (taskId) => 
    apiCall(`/task/status/${taskId}`)
}

export const patientAPI = {
  getDashboard: () => apiCall('/patient/dashboard'),
  
  getDoctors: (departmentId = null) => {
    let url = '/patient/doctors'
    if (departmentId) url += `?department_id=${departmentId}`
    return apiCall(url)
  },

  getAvailableDates: (doctorId) => 
    apiCall(`/patient/doctor/${doctorId}/available-dates`),

  getDoctorAvailability: (doctorId, date) => 
    apiCall(`/patient/doctor/${doctorId}/availability?date=${date}`),

  bookAppointment: (doctorId, data) => 
    apiCall(`/patient/book/${doctorId}`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  rescheduleAppointment: (appointmentId, data) => 
    apiCall(`/patient/appointment/${appointmentId}/reschedule`, {
      method: 'PUT',
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

  getAnalytics: () => apiCall('/patient/analytics'),

  // Export Task
  exportHistory: (startDate, endDate) => 
    apiCall('/task/export-patient-csv', {
      method: 'POST',
      body: JSON.stringify({ start_date: startDate, end_date: endDate })
    }),
    
  getTaskStatus: (taskId) => 
    apiCall(`/task/status/${taskId}`)
}

export const departmentsAPI = {
  getDepartments: () => apiCall('/departments')
}

export const paymentAPI = {
  processPayment: (paymentId) => 
    apiCall(`/payment/${paymentId}/pay`, { method: 'POST' })
}