<template>
  <div class="d-flex" style="min-height: 100vh; background-color: #f8f9fa;">
    <!-- Sidebar -->
    <nav class="bg-primary text-white p-4" style="width: 240px; min-height: 100vh; overflow-y: auto;">
      <div class="nav flex-column gap-2">
        <RouterLink to="/doctor/dashboard" class="nav-link text-white">
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
        <RouterLink to="/doctor/analytics" class="nav-link text-white active">
          <span class="me-2">📈</span>Analytics
        </RouterLink>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="flex-grow-1">
      <div class="bg-white border-bottom p-4 mb-4">
        <h2 class="mb-1">📈 My Analytics</h2>
        <p class="text-muted mb-0">Performance and appointment statistics.</p>
      </div>

      <div class="container-fluid px-4">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else class="row g-4">
          <div class="col-lg-6">
            <div class="card h-100">
              <div class="card-header bg-white border-bottom">
                <h5 class="mb-0">📅 Appointments (Last 7 Days)</h5>
              </div>
              <div class="card-body">
                <div class="chart-container">
                  <canvas ref="chartWeek"></canvas>
                </div>
              </div>
            </div>
          </div>
          <div class="col-lg-6">
            <div class="card h-100">
              <div class="card-header bg-white border-bottom">
                <h5 class="mb-0">📊 Appointment Status</h5>
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
import { doctorAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(true)
const chartWeek = ref(null)
const chartStatus = ref(null)

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
    const data = await doctorAPI.getAnalytics()
    
    loading.value = false
    await nextTick()

    if (chartWeek.value) {
      new Chart(chartWeek.value.getContext('2d'), {
        type: 'bar',
        data: { 
          labels: data.last_7_days.labels, 
          datasets: [{ 
            label: 'Appointments', 
            data: data.last_7_days.values, 
            backgroundColor: '#007bff',
            borderRadius: 4
          }] 
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { beginAtZero: true, ticks: { stepSize: 1 } }
          }
        }
      })
    }

    if (chartStatus.value) {
      new Chart(chartStatus.value.getContext('2d'), {
        type: 'doughnut',
        data: { 
          labels: data.appointment_status.labels, 
          datasets: [{ 
            data: data.appointment_status.values, 
            backgroundColor: ['#007bff', '#28a745', '#dc3545'] 
          }] 
        },
        options: { responsive: true, maintainAspectRatio: false }
      })
    }

  } catch (error) {
    console.error('Analytics error:', error)
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

/* Dedicated container to prevent infinite expansion */
.chart-container {
  position: relative;
  height: 350px;
  width: 100%;
}
</style>