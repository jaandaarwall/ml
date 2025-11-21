<template>
  <div class="d-flex" style="min-height: 100vh;">
    <!-- Sidebar -->
    <nav class="bg-primary text-white p-4" style="width: 250px; min-height: 100vh; overflow-y: auto;">
      <ul class="nav flex-column gap-2">
        <li class="nav-item">
          <RouterLink to="/patient/dashboard" class="nav-link text-white">
            <span>📊 Dashboard</span>
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/patient/book-appointment" class="nav-link text-white">
            <span>🔍 Find Doctors</span>
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/patient/appointments" class="nav-link text-white">
            <span>📅 My Appointments</span>
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/patient/history" class="nav-link text-white">
            <span>📋 Medical History</span>
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/patient/profile" class="nav-link text-white">
            <span>👤 My Profile</span>
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/patient/analytics" class="nav-link text-white active">
            <span>📈 Analytics</span>
          </RouterLink>
        </li>
      </ul>
    </nav>

    <!-- Main Content -->
    <div class="flex-grow-1">
      <!-- Header -->
      <div class="bg-white border-bottom p-4 mb-4">
        <h1 class="mb-1">📈 My Analytics</h1>
        <p class="text-muted mb-0">Overview of your medical history statistics</p>
      </div>

      <!-- Content -->
      <div class="container-fluid px-4 pb-5">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else class="row g-4">
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
          <div class="col-lg-6">
            <div class="card h-100">
              <div class="card-header bg-light">
                <h5 class="mb-0">Status Distribution</h5>
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
import { patientAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const chartMonth = ref(null)
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
    const data = await patientAPI.getAnalytics()
    
    loading.value = false
    await nextTick()

    if (chartMonth.value) {
      new Chart(chartMonth.value.getContext('2d'), {
        type: 'bar',
        data: { 
          labels: data.appointments_per_month.labels, 
          datasets: [{ 
            label: 'Appointments', 
            data: data.appointments_per_month.values, 
            backgroundColor: '#007bff' 
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
        type: 'pie',
        data: { 
          labels: data.status_distribution.labels, 
          datasets: [{ 
            data: data.status_distribution.values, 
            backgroundColor: ['#007bff', '#28a745', '#dc3545'] 
          }] 
        },
        options: { responsive: true, maintainAspectRatio: false }
      })
    }
  } catch (error) {
    console.error('Failed to load analytics:', error)
    loading.value = false
  }
})
</script>

<style scoped>
.nav-link {
  padding: 10px 15px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link.active {
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: 600;
  border-left: 4px solid #fbbf24;
}

/* Dedicated container to prevent infinite expansion */
.chart-container {
  position: relative;
  height: 350px;
  width: 100%;
}
</style>