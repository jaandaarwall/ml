<!-- views/patient/Appointments.vue -->
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
          <RouterLink to="/patient/appointments" class="nav-link text-white active">
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
          <RouterLink to="/patient/analytics" class="nav-link text-white">
            <span>📈 Analytics</span>
          </RouterLink>
        </li>
      </ul>
    </nav>

    <!-- Main Content -->
    <div class="flex-grow-1">
      <div class="bg-white border-bottom p-4 mb-4 d-flex justify-content-between align-items-center">
        <div>
          <h1 class="mb-1">📅 My Appointments</h1>
          <p class="text-muted mb-0">View and manage your appointments</p>
        </div>
        <div class="d-flex gap-2">
          <!-- Sorting Dropdown -->
          <select v-model="sortOrder" class="form-select">
            <option value="desc">Newest First</option>
            <option value="asc">Oldest First</option>
          </select>
          <RouterLink to="/patient/book-appointment" class="btn btn-primary">
            ➕ Book New
          </RouterLink>
        </div>
      </div>

      <div class="container-fluid px-4 pb-5">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger">
          {{ error }}
        </div>

        <div v-else-if="sortedAppointments.length === 0" class="alert alert-info">
          No appointments yet. <RouterLink to="/patient/book-appointment">Book one now!</RouterLink>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Date</th>
                <th>Time</th>
                <th>Doctor</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="apt in sortedAppointments" :key="apt.id">
                <td>#{{ apt.id }}</td>
                <td>{{ apt.date }}</td>
                <td>{{ apt.time }}</td>
                <td>{{ apt.doctor_name }}</td>
                <td>
                  <span :class="['badge', getStatusClass(apt.status)]">
                    {{ apt.status }}
                  </span>
                </td>
                <td>
                  <!-- Cancel Action -->
                  <button 
                    v-if="apt.status === 'Booked'"
                    @click="cancelAppointment(apt.id)"
                    class="btn btn-sm btn-danger me-2"
                  >
                    ❌ Cancel
                  </button>
                  
                  <!-- Diagnosis Action -->
                  <button 
                    v-if="apt.status === 'Completed' && apt.diagnosis"
                    @click="showDiagnosis(apt)"
                    class="btn btn-sm btn-info text-white"
                  >
                    📋 View Treatment
                  </button>
                  
                  <span v-if="apt.status !== 'Booked' && !apt.diagnosis" class="text-muted">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Treatment Detail Modal -->
    <div v-if="selectedTreatment" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">Treatment Details</h5>
            <button type="button" class="btn-close" @click="selectedTreatment = null"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <h6 class="fw-bold text-primary">📋 Diagnosis:</h6>
              <p class="bg-light p-2 rounded border">{{ selectedTreatment.diagnosis || 'N/A' }}</p>
            </div>
            <div class="mb-3">
              <h6 class="fw-bold text-success">💊 Prescription:</h6>
              <p class="bg-light p-2 rounded border" style="white-space: pre-line;">{{ selectedTreatment.prescription || 'N/A' }}</p>
            </div>
            <div>
              <h6 class="fw-bold text-secondary">📝 Doctor's Notes:</h6>
              <p class="bg-light p-2 rounded border" style="white-space: pre-line;">{{ selectedTreatment.notes || 'N/A' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { patientAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const appointments = ref([])
const sortOrder = ref('desc')
const selectedTreatment = ref(null)

const sortedAppointments = computed(() => {
  return [...appointments.value].sort((a, b) => {
    const dateA = new Date(`${a.date} ${a.time}`)
    const dateB = new Date(`${b.date} ${b.time}`)
    return sortOrder.value === 'asc' ? dateA - dateB : dateB - dateA
  })
})

const getStatusClass = (status) => {
  const classes = {
    'Booked': 'bg-info',
    'Completed': 'bg-success',
    'Cancelled': 'bg-danger'
  }
  return classes[status] || 'bg-secondary'
}

const fetchAppointments = async () => {
  try {
    const response = await patientAPI.getAppointments()
    appointments.value = response
  } catch (err) {
    error.value = err.message || 'Failed to load appointments'
  } finally {
    loading.value = false
  }
}

const cancelAppointment = async (appointmentId) => {
  if (!confirm('Are you sure you want to cancel this appointment?')) return

  try {
    await patientAPI.cancelAppointment(appointmentId)
    fetchAppointments()
  } catch (err) {
    error.value = err.message || 'Failed to cancel appointment'
  }
}

const showDiagnosis = (apt) => {
  selectedTreatment.value = {
    diagnosis: apt.diagnosis,
    prescription: apt.prescription,
    notes: apt.notes
  }
}

onMounted(fetchAppointments)
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