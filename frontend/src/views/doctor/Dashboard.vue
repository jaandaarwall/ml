<!-- views/doctor/Dashboard.vue -->
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
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="apt in dashboard.upcoming_appointments" :key="apt.id">
                      <td><strong>{{ apt.date }}</strong></td>
                      <td>{{ apt.time }}</td>
                      <td>{{ apt.patient_name }}</td>
                    </tr>
                  </tbody>
                </table>
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

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
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
