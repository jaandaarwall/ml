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
        <RouterLink to="/admin/analytics" class="nav-link text-white mb-2 active-nav">
          📈 Reports
        </RouterLink>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="flex-grow-1 d-flex flex-column overflow-auto">
      <!-- Header -->
      <div class="bg-white border-bottom p-4">
        <h1 class="mb-1">📈 Analytics Dashboard</h1>
        <p class="text-muted mb-0">View system statistics and reports</p>
      </div>

      <!-- Content -->
      <div class="flex-grow-1 p-4 overflow-auto">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

        <div v-else class="row g-4">
          <!-- Appointments Chart -->
          <div class="col-lg-6">
            <div class="card h-100">
              <div class="card-header bg-light">
                <h5 class="mb-0">Appointments per Month</h5>
              </div>
              <div class="card-body">
                <div class="chart-container">
                  <canvas ref="chartMonth"></canvas>
                </div>
              </div>
            </div>
          </div>

          <!-- Doctors per Department -->
          <div class="col-lg-6">
            <div class="card h-100">
              <div class="card-header bg-light">
                <h5 class="mb-0">Doctors per Department</h5>
              </div>
              <div class="card-body">
                <div class="chart-container">
                  <canvas ref="chartDept"></canvas>
                </div>
              </div>
            </div>
          </div>

          <!-- Appointment Status -->
          <div class="col-lg-6">
            <div class="card h-100">
              <div class="card-header bg-light">
                <h5 class="mb-0">Appointment Status Summary</h5>
              </div>
              <div class="card-body">
                <div class="chart-container">
                  <canvas ref="chartStatus"></canvas>
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
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { Chart } from 'chart.js/auto'
import { adminAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const chartMonth = ref(null)
const chartDept = ref(null)
const chartStatus = ref(null)

const fetchAnalytics = async () => {
  try {
    const data = await adminAPI.getAnalytics()

    loading.value = false
    await nextTick()

    if (chartMonth.value) {
      new Chart(chartMonth.value.getContext('2d'), {
        type: 'line',
        data: {
          labels: data.appointments_per_month.labels,
          datasets: [{
            label: 'Appointments',
            data: data.appointments_per_month.values,
            borderColor: '#0d6efd',
            backgroundColor: 'rgba(13, 110, 253, 0.1)',
            tension: 0.1,
            fill: true
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      })
    }

    if (chartDept.value) {
      new Chart(chartDept.value.getContext('2d'), {
        type: 'bar',
        data: {
          labels: data.doctors_per_department.labels,
          datasets: [{
            label: 'Doctors',
            data: data.doctors_per_department.values,
            backgroundColor: '#198754'
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      })
    }

    if (chartStatus.value) {
      new Chart(chartStatus.value.getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: data.appointment_status_summary.labels,
          datasets: [{
            data: data.appointment_status_summary.values,
            backgroundColor: ['#0d6efd', '#198754', '#dc3545']
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      })
    }

  } catch (err) {
    error.value = err.message || 'Failed to load analytics'
    loading.value = false
  }
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

onMounted(fetchAnalytics)
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

.nav-link.active-nav {
  background-color: rgba(255, 255, 255, 0.2);
  border-left: 4px solid #ffc107;
  padding-left: 1rem;
  font-weight: 600;
}

/* Dedicated container to prevent infinite expansion */
.chart-container {
  position: relative;
  height: 350px;
  width: 60%;
}
</style>