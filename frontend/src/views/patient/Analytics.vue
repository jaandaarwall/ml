<template>
  <div class="d-flex" style="min-height: 100vh;">
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
                <h5 class="mb-0">Appointments & Cancellations per Month</h5>
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
                <h5 class="mb-0">💰 Money Spent vs Date</h5>
              </div>
              <div class="card-body">
                <div class="chart-container">
                  <canvas ref="chartMoney"></canvas>
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
const chartMoney = ref(null)

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
          datasets: [
            { 
              label: 'Total Appointments', 
              data: data.appointments_per_month.total, 
              backgroundColor: '#007bff',
              borderColor: '#007bff',
              borderWidth: 1
            },
            { 
              label: 'Cancelled', 
              data: data.appointments_per_month.cancelled, 
              backgroundColor: '#dc3545',
              borderColor: '#dc3545',
              borderWidth: 1
            }
          ] 
        },
        options: { 
          responsive: true, 
          maintainAspectRatio: false,
          scales: {
            y: { beginAtZero: true, ticks: { stepSize: 1 } }
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

    if (chartMoney.value) {
      new Chart(chartMoney.value.getContext('2d'), {
        type: 'line',
        data: { 
          labels: data.money_spent_vs_date.labels, 
          datasets: [{ 
            label: 'Amount Spent (₹)', 
            data: data.money_spent_vs_date.values, 
            backgroundColor: 'rgba(40, 167, 69, 0.2)',
            borderColor: '#28a745',
            borderWidth: 2,
            fill: true,
            tension: 0.3
          }] 
        },
        options: { 
          responsive: true, 
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: function(value) {
                  return '₹' + value;
                }
              }
            }
          }
        }
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