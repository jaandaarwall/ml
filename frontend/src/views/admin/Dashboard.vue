<template>
  <div class="d-flex" style="height: 100vh;">
    <!-- Sidebar Navigation -->
    <div class="bg-primary text-white p-4" style="width: 250px; overflow-y: auto;">      
      <nav class="nav flex-column">
        <RouterLink to="/admin/dashboard" class="nav-link text-white mb-2">
          📊 Dashboard
        </RouterLink>
        <RouterLink to="/admin/doctors" class="nav-link text-white mb-2">
          👨‍⚕️ Manage Doctors
        </RouterLink>
        <RouterLink to="/admin/patients" class="nav-link text-white mb-2">
          👥 Manage Patients
        </RouterLink>
        <RouterLink to="/admin/appointments" class="nav-link text-white mb-2">
          📅 All Appointments
        </RouterLink>
        <RouterLink to="/admin/transactions" class="nav-link text-white mb-2">
          💰 Transactions
        </RouterLink>
        <RouterLink to="/admin/analytics" class="nav-link text-white mb-2">
          📈 Reports
        </RouterLink>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="flex-grow-1 d-flex flex-column overflow-auto">
      <!-- Header -->
      <div class="bg-white border-bottom p-4">
        <h1 class="mb-1">⚙️ Admin Dashboard</h1>
        <p class="text-muted mb-0">Welcome back, System Administrator!</p>
      </div>

      <!-- Content -->
      <div class="flex-grow-1 p-4 overflow-auto">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger">
          {{ error }}
        </div>

        <div v-else>
          <!-- Statistics Grid -->
          <div class="row g-4 mb-4">
            <div class="col-md-3">
              <div class="card border-start border-primary border-4 h-100">
                <div class="card-body">
                  <h6 class="text-muted text-uppercase small">Total Doctors</h6>
                  <h2 class="mb-0">{{ dashboardData.total_doctors }}</h2>
                  <p class="text-muted small mt-2">Active doctors in system</p>
                </div>
              </div>
            </div>

            <div class="col-md-3">
              <div class="card border-start border-success border-4 h-100">
                <div class="card-body">
                  <h6 class="text-muted text-uppercase small">Total Patients</h6>
                  <h2 class="mb-0">{{ dashboardData.total_patients }}</h2>
                  <p class="text-muted small mt-2">Registered patients</p>
                </div>
              </div>
            </div>

            <div class="col-md-3">
              <div class="card border-start border-warning border-4 h-100">
                <div class="card-body">
                  <h6 class="text-muted text-uppercase small">Total Appointments</h6>
                  <h2 class="mb-0">{{ dashboardData.total_appointments }}</h2>
                  <p class="text-muted small mt-2">All appointments</p>
                </div>
              </div>
            </div>

            <div class="col-md-3">
              <div class="card border-start border-danger border-4 h-100">
                <div class="card-body">
                  <h6 class="text-muted text-uppercase small">Today's Appointments</h6>
                  <h2 class="mb-0">{{ dashboardData.today_appointments }}</h2>
                  <p class="text-muted small mt-2">Scheduled today</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="card mb-4">
            <div class="card-header bg-light">
              <h5 class="mb-0">⚡ Quick Actions</h5>
            </div>
            <div class="card-body">
              <div class="row g-2">
                <div class="col-md-3">
                  <RouterLink to="/admin/doctors" class="btn btn-primary w-100">
                    ➕ Add New Doctor
                  </RouterLink>
                </div>
                <div class="col-md-3">
                  <RouterLink to="/admin/appointments" class="btn btn-success w-100">
                    👁️ View All Appointments
                  </RouterLink>
                </div>
                <div class="col-md-3">
                  <RouterLink to="/admin/search" class="btn btn-info w-100">
                    🔍 Search Patients
                  </RouterLink>
                </div>
                <div class="col-md-3">
                  <RouterLink to="/admin/analytics" class="btn btn-warning w-100">
                    📊 View Analytics
                  </RouterLink>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Appointments -->
          <div class="card">
            <div class="card-header bg-light d-flex justify-content-between align-items-center">
              <h5 class="mb-0">⏰ Recent Appointments</h5>
              <RouterLink to="/admin/appointments" class="btn btn-sm btn-outline-primary">
                View All →
              </RouterLink>
            </div>
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="table-light">
                  <tr>
                    <th>ID</th>
                    <th>Patient</th>
                    <th>Doctor</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="recentAppointments.length === 0">
                    <td colspan="6" class="text-center text-muted py-4">
                      No appointments found
                    </td>
                  </tr>
                  <tr v-for="(apt, index) in recentAppointments" :key="apt.id">
                    <td><span class="badge bg-light text-dark">#{{ index + 1 }}</span></td>
                    <td class="fw-bold">{{ apt.patient_name }}</td>
                    <td>Dr. {{ apt.doctor_name }}</td>
                    <td>{{ apt.appointment_date }}</td>
                    <td>{{ apt.appointment_time }}</td>
                    <td>
                      <span v-if="apt.status === 'Completed'" class="badge bg-success">
                        {{ apt.status }}
                      </span>
                      <span v-else-if="apt.status === 'Booked'" class="badge bg-info">
                        {{ apt.status }}
                      </span>
                      <span v-else class="badge bg-danger">
                        {{ apt.status }}
                      </span>
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { adminAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const recentAppointments = ref([])

const dashboardData = ref({
  total_doctors: 0,
  total_patients: 0,
  total_appointments: 0,
  today_appointments: 0
})

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

const fetchDashboard = async () => {
  try {
    const response = await adminAPI.getDashboard()
    dashboardData.value = response
    loading.value = false
  } catch (err) {
    error.value = err.message || 'Failed to load dashboard'
    loading.value = false
  }
}

const fetchAppointments = async () => {
  try {
    const response = await adminAPI.getAppointments()
    recentAppointments.value = response.slice(0, 5)
  } catch (err) {
    console.error('Failed to load appointments', err)
  }
}

onMounted(() => {
  fetchDashboard()
  fetchAppointments()
})
</script>

<style scoped>
.nav-link {
  transition: all 0.3s ease;
  padding: 0.75rem 0.5rem;
  border-radius: 0.375rem;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  padding-left: 1rem;
}

.nav-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
  border-left: 4px solid #ffc107;
  padding-left: 1rem;
  font-weight: 600;
}
</style>