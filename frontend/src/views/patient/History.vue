<!-- views/patient/History.vue -->
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
          <RouterLink to="/patient/history" class="nav-link text-white active">
            <span>📋 Medical History</span>
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/patient/profile" class="nav-link text-white">
            <span>👤 My Profile</span>
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/patient/analytics" class="nav-link text-white">
            <span>📈 Analytics</span>
          </RouterLink>
        </li>
      </ul>
    </nav>

    <!-- Main Content -->
    <div class="flex-grow-1">
      <!-- Header -->
      <div class="bg-white border-bottom p-4 mb-4">
        <h1 class="mb-1">⏰ My Medical History</h1>
        <p class="text-muted mb-0">A complete record of your past consultations and treatments.</p>
      </div>

      <!-- Content -->
      <div class="container-fluid px-4 pb-5">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger">
          {{ error }}
        </div>

        <div v-else-if="history.length === 0" class="alert alert-info">
          No medical history yet
        </div>

        <div v-else class="accordion" id="historyAccordion">
          <div v-for="(record, index) in history" :key="record.id" class="accordion-item">
            <h2 class="accordion-header">
              <button 
                class="accordion-button" 
                type="button" 
                :class="{ collapsed: index !== 0 }"
                :data-bs-target="`#history${index}`" 
                data-bs-toggle="collapse"
              >
                <strong>{{ record.date }}</strong> - Consultation with <strong>Dr. {{ record.doctor_name }}</strong> ({{ record.department }})
              </button>
            </h2>
            <div :id="`history${index}`" class="accordion-collapse collapse" :class="{ show: index === 0 }">
              <div class="accordion-body">
                <div class="row mb-3">
                  <div class="col-md-6">
                    <h6 class="fw-bold">📋 Diagnosis:</h6>
                    <p>{{ record.diagnosis || 'N/A' }}</p>
                  </div>
                  <div class="col-md-6">
                    <h6 class="fw-bold">💊 Prescription:</h6>
                    <p>{{ record.prescription || 'N/A' }}</p>
                  </div>
                </div>

                <div class="mb-3">
                  <h6 class="fw-bold">📝 Notes from Doctor:</h6>
                  <p>{{ record.notes || 'N/A' }}</p>
                </div>

                <div v-if="record.follow_up_required" class="alert alert-warning mb-0">
                  <strong>⚠️ Follow-up Required:</strong> Yes, on a specified date
                  <span v-if="record.follow_up_date"> ({{ record.follow_up_date }})</span>
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
import { patientAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const history = ref([])

const fetchHistory = async () => {
  try {
    const response = await patientAPI.getHistory()
    history.value = response
  } catch (err) {
    error.value = err.message || 'Failed to load history'
  } finally {
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

onMounted(fetchHistory)
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
</style>
