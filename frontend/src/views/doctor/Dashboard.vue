<template>
  <div class="d-flex" style="min-height: 100vh; background-color: #f8f9fa;">
    <!-- Sidebar -->
    <nav class="bg-primary text-white p-4" style="width: 240px; min-height: 100vh; overflow-y: auto;">
      <div class="nav flex-column gap-2">
        <RouterLink to="/doctor/dashboard" class="nav-link text-white active">
          <span class="me-2">📊</span>Dashboard
        </RouterLink>
        <RouterLink to="/doctor/appointments" class="nav-link text-white">
          <span class="me-2">📅</span>My Appointments
        </RouterLink>
        <RouterLink to="/doctor/patients" class="nav-link text-white">
          <span class="me-2">👥</span>My Patients
        </RouterLink>
        <RouterLink to="/doctor/availability" class="nav-link text-white">
          <span class="me-2">⏰</span>Set Availability
        </RouterLink>
        <RouterLink to="/doctor/profile" class="nav-link text-white">
          <span class="me-2">👤</span>My Profile
        </RouterLink>
        <RouterLink to="/doctor/analytics" class="nav-link text-white">
          <span class="me-2">📈</span>Analytics
        </RouterLink>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="flex-grow-1">
      <!-- Header -->
      <div class="bg-white border-bottom p-4 mb-4">
        <h2 class="mb-1">👨‍⚕️ Doctor Dashboard</h2>
        <p class="text-muted mb-0">Welcome, Dr. {{ doctorName }} | {{ departmentName }}</p>
      </div>

      <!-- Content -->
      <div class="container-fluid px-4">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else>
          <!-- Statistics Cards -->
          <div class="row mb-4">
            <div class="col-md-4 mb-3">
              <div class="card border-left-primary h-100">
                <div class="card-body">
                  <div class="text-muted text-uppercase small mb-2">Today's Appointments</div>
                  <div class="h3 mb-0">{{ dashboard.today_appointments.length }}</div>
                </div>
              </div>
            </div>
            <div class="col-md-4 mb-3">
              <div class="card border-left-success h-100">
                <div class="card-body">
                  <div class="text-muted text-uppercase small mb-2">Upcoming Appointments</div>
                  <div class="h3 mb-0">{{ dashboard.upcoming_appointments.length }}</div>
                </div>
              </div>
            </div>
            <div class="col-md-4 mb-3">
              <div class="card border-left-info h-100">
                <div class="card-body">
                  <div class="text-muted text-uppercase small mb-2">Total Patients</div>
                  <div class="h3 mb-0">{{ dashboard.total_patients }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Today's Appointments -->
          <div class="card mb-4">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h5 class="mb-0">📅 Today's Appointments</h5>
              <RouterLink to="/doctor/appointments" class="btn btn-outline-primary btn-sm">
                View All
              </RouterLink>
            </div>
            <div class="card-body">
              <div v-if="dashboard.today_appointments.length === 0" class="text-center py-4 text-muted">
                <p>📭 No appointments scheduled for today</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-sm table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Time</th>
                      <th>Patient</th>
                      <th>Status</th>
                      <th>Reason</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="apt in dashboard.today_appointments" :key="apt.id">
                      <td><strong>{{ apt.time }}</strong></td>
                      <td>{{ apt.patient_name }}</td>
                      <td>
                        <span class="badge bg-info">{{ apt.status }}</span>
                      </td>
                      <td>{{ apt.reason }}</td>
                      <td>
                        <div class="btn-group">
                          <RouterLink v-if="apt.status === 'Booked' || apt.status === 'Completed'" 
                            :to="`/doctor/appointment/${apt.id}/treatment`"
                            :class="['btn', 'btn-sm', apt.status === 'Completed' ? 'btn-warning' : 'btn-success']">
                            {{ apt.status === 'Completed' ? '✏️ Edit' : '💊 Treat' }}
                          </RouterLink>
                          <button @click="openPatientDetails(apt.patient_id)" 
                                  class="btn btn-sm btn-info text-white">
                            👤 Info
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Upcoming Appointments -->
          <div class="card">
            <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
              <h5 class="mb-0">📆 Upcoming Appointments</h5>
              <RouterLink to="/doctor/appointments" class="btn btn-outline-primary btn-sm">
                View All
              </RouterLink>
            </div>
            <div class="card-body">
              <div v-if="dashboard.upcoming_appointments.length === 0" class="text-center py-4 text-muted">
                <p>📭 No upcoming appointments</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-sm table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Date</th>
                      <th>Time</th>
                      <th>Patient</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="apt in dashboard.upcoming_appointments" :key="apt.id">
                      <td><strong>{{ apt.date }}</strong></td>
                      <td>{{ apt.time }}</td>
                      <td>{{ apt.patient_name }}</td>
                      <td>
                        <div class="btn-group">
                          <RouterLink v-if="apt.status === 'Booked' || apt.status === 'Completed'" 
                            :to="`/doctor/appointment/${apt.id}/treatment`"
                            :class="['btn', 'btn-sm', apt.status === 'Completed' ? 'btn-warning' : 'btn-success']">
                            {{ apt.status === 'Completed' ? '✏️ Edit' : '💊 Treat' }}
                          </RouterLink>
                          <button @click="openPatientDetails(apt.patient_id)" 
                                  class="btn btn-sm btn-info text-white">
                            👤 Info
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Patient Details Modal -->
    <div v-if="showPatientModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-info text-white">
            <h5 class="modal-title">Patient Information</h5>
            <button type="button" class="btn-close" @click="showPatientModal = false"></button>
          </div>
          <div class="modal-body" style="max-height: 80vh; overflow-y: auto;">
            <div v-if="loadingHistory" class="text-center py-4">
              <div class="spinner-border text-info"></div>
            </div>
            
            <div v-else>
              <!-- Patient Personal Details -->
              <div class="card mb-4 border-info">
                <div class="card-header bg-light text-info fw-bold">
                  👤 Personal Details
                </div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-6">
                      <p class="mb-2"><strong>Name:</strong> {{ patientDetails.name }}</p>
                      <p class="mb-2"><strong>Age:</strong> {{ patientDetails.age || 'N/A' }} ({{ patientDetails.gender || 'N/A' }})</p>
                      <p class="mb-0"><strong>Blood Group:</strong> <span class="badge bg-danger">{{ patientDetails.blood_group || 'N/A' }}</span></p>
                    </div>
                    <div class="col-md-6">
                      <p class="mb-2"><strong>Email:</strong> {{ patientDetails.email }}</p>
                      <p class="mb-2"><strong>Phone:</strong> {{ patientDetails.phone || 'N/A' }}</p>
                      <p class="mb-0"><strong>DOB:</strong> {{ patientDetails.dob || 'N/A' }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Medical History -->
              <h5 class="mb-3 text-secondary">📋 Medical History</h5>
              <div v-if="patientHistory.length === 0" class="alert alert-warning">
                No previous treatment history found for this patient.
              </div>
              <div v-else>
                <div v-for="(record, index) in patientHistory" :key="index" class="card mb-3 border">
                  <div class="card-header bg-light d-flex justify-content-between align-items-center">
                    <strong>📅 {{ record.date }}</strong>
                    <button class="btn btn-sm btn-outline-primary" @click="toggleDiagnosis(index)">
                      {{ record.showDetails ? 'Hide' : 'Show' }} Diagnosis
                    </button>
                  </div>
                  <div v-if="record.showDetails" class="card-body">
                    <p><strong>📋 Diagnosis:</strong> {{ record.diagnosis }}</p>
                    <p><strong>💊 Prescription:</strong> {{ record.prescription }}</p>
                    <p class="mb-0"><strong>📝 Notes:</strong> {{ record.notes }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { doctorAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const doctorName = ref('')
const departmentName = ref('')
const dashboard = ref({
  today_appointments: [],
  upcoming_appointments: [],
  total_patients: 0
})

// Modal State
const showPatientModal = ref(false)
const loadingHistory = ref(false)
const patientHistory = ref([])
const patientDetails = ref({}) // Store patient info

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

const openPatientDetails = async (patientId) => {
  showPatientModal.value = true
  loadingHistory.value = true
  patientHistory.value = []
  patientDetails.value = {}
  
  try {
    const response = await doctorAPI.getPatientHistory(patientId)
    // Backend now returns { patient: {...}, history: [...] }
    patientDetails.value = response.patient
    patientHistory.value = response.history.map(record => ({ ...record, showDetails: false }))
  } catch (err) {
    console.error("Failed to load history", err)
  } finally {
    loadingHistory.value = false
  }
}

const toggleDiagnosis = (index) => {
  patientHistory.value[index].showDetails = !patientHistory.value[index].showDetails
}

onMounted(async () => {
  try {
    const dashResponse = await doctorAPI.getDashboard()
    dashboard.value = dashResponse
    
    const profileResponse = await doctorAPI.getProfile()
    doctorName.value = profileResponse.username
    departmentName.value = profileResponse.department
  } finally {
    loading.value = false
  }
})
</script>

<style>
.nav-link.active {
  background-color: rgba(255, 255, 255, 0.2) !important;
  border-left: 4px solid #ffc107;
  padding-left: calc(1rem - 4px) !important;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.border-left-primary {
  border-left: 4px solid #007bff !important;
}

.border-left-success {
  border-left: 4px solid #28a745 !important;
}

.border-left-info {
  border-left: 4px solid #17a2b8 !important;
}
</style>