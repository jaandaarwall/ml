<!-- views/doctor/Appointments.vue -->
<template>
  <div class="d-flex" style="min-height: 100vh; background-color: #f8f9fa;">
    <!-- Sidebar (same as dashboard) -->
    <nav class="bg-primary text-white p-4" style="width: 240px; min-height: 100vh; overflow-y: auto;">
      <div class="nav flex-column gap-2">
        <RouterLink to="/doctor/dashboard" class="nav-link text-white">
          <span class="me-2">📊</span>Dashboard
        </RouterLink>
        <RouterLink to="/doctor/appointments" class="nav-link text-white active">
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
      <div class="bg-white border-bottom p-4 mb-4">
        <h2 class="mb-1">📅 My Appointments</h2>
        <p class="text-muted mb-0">View and manage all your appointments.</p>
      </div>

      <div class="container-fluid px-4">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else class="card">
          <div class="card-body">
            <div v-if="appointments.length === 0" class="text-center py-5 text-muted">
              <p>No appointments found</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Patient</th>
                    <th>Reason</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="apt in appointments" :key="apt.id">
                    <td><strong>{{ apt.date }}</strong></td>
                    <td>{{ apt.time }}</td>
                    <td>{{ apt.patient_name }}</td>
                    <td>{{ apt.reason }}</td>
                    <td>
                      <span :class="['badge', getStatusClass(apt.status)]">
                        {{ apt.status }}
                      </span>
                    </td>
                    <td>
                      <RouterLink v-if="apt.status === 'Booked'" 
                        :to="`/doctor/appointment/${apt.id}/treatment`"
                        class="btn btn-sm btn-info">
                        ✏️ Treatment
                      </RouterLink>
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
import { doctorAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(true)
const appointments = ref([])

const getStatusClass = (status) => {
  const classes = {
    'Booked': 'bg-info',
    'Completed': 'bg-success',
    'Cancelled': 'bg-danger'
  }
  return classes[status] || 'bg-secondary'
}

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
    const response = await doctorAPI.getAppointments()
    appointments.value = response
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
</style>
