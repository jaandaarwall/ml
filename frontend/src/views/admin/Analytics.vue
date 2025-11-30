<template>
  <div class="d-flex" style="height: 100vh;">

    <div class="flex-grow-1 d-flex flex-column overflow-auto">
      <div class="bg-white border-bottom p-4">
        <h1 class="mb-1">📈 Analytics Dashboard</h1>
        <p class="text-muted mb-0">View system statistics and reports</p>
      </div>

      <div class="flex-grow-1 p-4 overflow-auto">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

        <div v-else class="row g-4">
          <div class="col-12">
            <div class="card h-100">
              <div class="card-header bg-light text-success">
                <h5 class="mb-0">💰 Monthly Revenue vs Refunds</h5>
              </div>
              <div class="card-body">
                <div class="chart-container">
                  <canvas ref="chartRevenue"></canvas>
                </div>
              </div>
            </div>
          </div>

          <div class="col-lg-6">
            <div class="card h-100">
              <div class="card-header bg-light">
                <h5 class="mb-0">Appointments vs Cancellations per Month</h5>
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
                <h5 class="mb-0">Doctors per Department</h5>
              </div>
              <div class="card-body">
                <div class="chart-container">
                  <canvas ref="chartDept"></canvas>
                </div>
              </div>
            </div>
          </div>

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

          <div class="col-lg-6">
            <div class="card h-100">
              <div class="card-header bg-light">
                <h5 class="mb-0">🏆 Top 10 Active Doctors (This Month)</h5>
              </div>
              <div class="card-body">
                <div class="chart-container">
                  <canvas ref="chartTopDocs"></canvas>
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
const chartRevenue = ref(null)
const chartTopDocs = ref(null)

const fetchAnalytics = async () => {
  try {
    const data = await adminAPI.getAnalytics()

    loading.value = false
    await nextTick()

    if (chartRevenue.value) {
      new Chart(chartRevenue.value.getContext('2d'), {
        type: 'bar',
        data: {
          labels: data.revenue_per_month.labels,
          datasets: [
            {
              label: 'Revenue (₹)',
              data: data.revenue_per_month.revenue,
              backgroundColor: 'rgba(40, 167, 69, 0.6)',
              borderColor: '#28a745',
              borderWidth: 1
            },
            {
              label: 'Refunds (₹)',
              data: data.revenue_per_month.refunded,
              backgroundColor: 'rgba(220, 53, 69, 0.6)',
              borderColor: '#dc3545',
              borderWidth: 1
            }
          ]
        },
        options: { 
          responsive: true, 
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: (value) => '₹' + value
              }
            }
          },
          plugins: {
            tooltip: {
              mode: 'index',
              intersect: false
            }
          }
        }
      })
    }

    if (chartMonth.value) {
      new Chart(chartMonth.value.getContext('2d'), {
        type: 'bar',
        data: {
          labels: data.appointments_per_month.labels,
          datasets: [
            {
              label: 'Total Appointments',
              data: data.appointments_per_month.total,
              backgroundColor: 'rgba(13, 110, 253, 0.6)',
              borderColor: '#0d6efd',
              borderWidth: 1
            },
            {
              label: 'Cancelled',
              data: data.appointments_per_month.cancelled,
              backgroundColor: 'rgba(220, 53, 69, 0.6)',
              borderColor: '#dc3545',
              borderWidth: 1
            }
          ]
        },
        options: { 
          responsive: true, 
          maintainAspectRatio: false,
          interaction: {
            mode: 'index',
            intersect: false,
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          }
        }
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
            backgroundColor: ['#0d6efd', '#198754', '#dc3545', '#ffc107', '#6c757d']
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      })
    }

    if (chartTopDocs.value) {
      new Chart(chartTopDocs.value.getContext('2d'), {
        type: 'bar',
        data: {
          labels: data.top_active_doctors.labels,
          datasets: [{
            label: 'Appointments Completed',
            data: data.top_active_doctors.values,
            backgroundColor: 'rgba(255, 193, 7, 0.6)',
            borderColor: '#ffc107',
            borderWidth: 1
          }]
        },
        options: { 
          indexAxis: 'y',
          responsive: true, 
          maintainAspectRatio: false,
          scales: {
            x: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          }
        }
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

.chart-container {
  position: relative;
  height: 350px;
  width: 100%;
}
</style>