<!-- views/doctor/Availability.vue -->
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
        <RouterLink to="/doctor/availability" class="nav-link text-white active">
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
        <h2 class="mb-1">⏰ Set Availability</h2>
        <p class="text-muted mb-0">Manage your available time slots for appointments.</p>
      </div>

      <div class="container-fluid px-4">
        <div class="row">
          <!-- Add New Availability Form -->
          <div class="col-lg-4 mb-4">
            <div class="card">
              <div class="card-header bg-white border-bottom">
                <h5 class="mb-0">Add New Availability</h5>
              </div>
              <div class="card-body">
                <form @submit.prevent="addAvailability">
                  <div class="mb-3">
                    <label class="form-label">Date</label>
                    <input v-model="newSlot.date" type="date" class="form-control" required>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Start Time</label>
                    <input v-model="newSlot.start_time" type="time" class="form-control" required>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">End Time</label>
                    <input v-model="newSlot.end_time" type="time" class="form-control" required>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Total Seats</label>
                    <input v-model.number="newSlot.total_seats" type="number" class="form-control" value="30">
                  </div>
                  <button type="submit" class="btn btn-primary w-100">
                    Add Availability
                  </button>
                </form>
              </div>
            </div>
          </div>

          <!-- Current Availability -->
          <div class="col-lg-8 mb-4">
            <div class="card">
              <div class="card-header bg-white border-bottom">
                <h5 class="mb-0">Your Current Availability</h5>
              </div>
              <div class="card-body">
                <div v-if="loading" class="text-center py-5">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </div>
                <div v-else-if="availabilities.length === 0" class="text-center py-5 text-muted">
                  <p>No availability slots added yet</p>
                </div>
                <div v-else class="table-responsive">
                  <table class="table table-hover mb-0">
                    <thead class="table-light">
                      <tr>
                        <th>Date</th>
                        <th>Start Time</th>
                        <th>End Time</th>
                        <th>Seats</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="avail in availabilities" :key="avail.id">
                        <td><strong>{{ avail.date }}</strong></td>
                        <td>{{ avail.start_time }}</td>
                        <td>{{ avail.end_time }}</td>
                        <td>{{ avail.total_seats }}</td>
                        <td>
                          <button @click="deleteAvailability(avail.id)" class="btn btn-sm btn-danger">
                            🗑️
                          </button>
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
const availabilities = ref([])
const newSlot = ref({
  date: '',
  start_time: '',
  end_time: '',
  total_seats: 30
})

const fetchAvailabilities = async () => {
  try {
    const response = await doctorAPI.getAvailability()
    availabilities.value = response
  } finally {
    loading.value = false
  }
}

const addAvailability = async () => {
  try {
    await doctorAPI.addAvailability(newSlot.value)
    newSlot.value = { date: '', start_time: '', end_time: '', total_seats: 30 }
    fetchAvailabilities()
  } catch (err) {
    alert(err.message)
  }
}

const deleteAvailability = async (id) => {
  if (confirm('Delete this availability slot?')) {
    try {
      await doctorAPI.deleteAvailability(id)
      fetchAvailabilities()
    } catch (err) {
      alert(err.message)
    }
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

onMounted(fetchAvailabilities)
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

