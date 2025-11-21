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
      <!-- Header -->
      <div class="bg-white border-bottom p-4 mb-4 d-flex justify-content-between align-items-center">
        <div>
          <h1 class="mb-1">📅 My Appointments</h1>
          <p class="text-muted mb-0">View and manage your appointments</p>
        </div>
        <RouterLink to="/patient/book-appointment" class="btn btn-primary">
          ➕ Book New Appointment
        </RouterLink>
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

        <div v-else-if="appointments.length === 0" class="alert alert-info">
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
                <th>Specialization</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="apt in appointments" :key="apt.id">
                <td>#{{ apt.id }}</td>
                <td>{{ apt.date }}</td>
                <td>{{ apt.time }}</td>
                <td>{{ apt.doctor_name }}</td>
                <td>
                  <span class="badge bg-info">{{ apt.department }}</span>
                </td>
                <td>
                  <span :class="['badge', getStatusClass(apt.status)]">
                    {{ apt.status }}
                  </span>
                </td>
                <td>
                  <button 
                    v-if="apt.status === 'Booked'"
                    @click="cancelAppointment(apt.id)"
                    class="btn btn-sm btn-danger"
                  >
                    ❌ Cancel
                  </button>
                  <span v-else class="text-muted">-</span>
                </td>
              </tr>
            </tbody>
          </table>
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
const appointments = ref([])

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

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
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
